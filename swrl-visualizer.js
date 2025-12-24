/**
 * SWRL to DOT Converter - JavaScript version
 * Converts SWRL (Semantic Web Rule Language) rules to DOT graph format
 */

class SWRLToDOT {
    constructor() {
        this.variables = new Set();
        this.classes = {}; // variable -> class info array
        this.properties = []; // property relationships
    }

    /**
     * Parse SWRL rule into antecedent and consequent atoms
     * @param {string} rule - SWRL rule string
     * @returns {Object} Object with antecedent and consequent arrays
     */
    parseSWRLRule(rule) {
        // Split by arrow
        const parts = rule.split('->');
        if (parts.length !== 2) {
            throw new Error("Invalid SWRL rule: missing '->' separator");
        }

        const antecedent = parts[0].trim();
        const consequent = parts[1].trim();

        // Parse atoms (separated by ^)
        const antecedentAtoms = antecedent
            .split(/\s*\^\s*/)
            .map(atom => atom.trim())
            .filter(atom => atom.length > 0);
        
        const consequentAtoms = consequent
            .split(/\s*\^\s*/)
            .map(atom => atom.trim())
            .filter(atom => atom.length > 0);

        return { antecedentAtoms, consequentAtoms };
    }

    /**
     * Parse a single SWRL atom
     * @param {string} atom - SWRL atom string
     * @returns {Object} Parsed atom object
     */
    parseAtom(atom) {
        // Pattern for class atoms: prefix:ClassName(?var)
        const classPattern = /(\w+):(\w+)\((\?\w+)\)/;
        // Pattern for property atoms: prefix:propertyName(?var1, ?var2) or (?var1, literal)
        const propertyPattern = /(\w+):(\w+)\((\?\w+),\s*(.+?)\)/;

        const classMatch = atom.match(classPattern);
        if (classMatch) {
            return {
                type: 'class',
                prefix: classMatch[1],
                class: classMatch[2],
                variable: classMatch[3]
            };
        }

        const propertyMatch = atom.match(propertyPattern);
        if (propertyMatch) {
            return {
                type: 'property',
                prefix: propertyMatch[1],
                property: propertyMatch[2],
                subject: propertyMatch[3],
                object: propertyMatch[4].trim()
            };
        }

        throw new Error(`Cannot parse atom: ${atom}`);
    }

    /**
     * Generate DOT graph from SWRL rule
     * @param {string} rule - SWRL rule string
     * @returns {string} DOT graph representation
     */
    generateDOT(rule) {
        // Reset state
        this.variables = new Set();
        this.classes = {};
        this.properties = [];

        // Parse rule
        const { antecedentAtoms, consequentAtoms } = this.parseSWRLRule(rule);

        // Process all atoms
        const allAtoms = [];
        
        for (const atom of antecedentAtoms) {
            const parsed = this.parseAtom(atom);
            parsed.part = 'antecedent';
            allAtoms.push(parsed);
        }

        for (const atom of consequentAtoms) {
            const parsed = this.parseAtom(atom);
            parsed.part = 'consequent';
            allAtoms.push(parsed);
        }

        // Extract variables, classes, and properties
        for (const atom of allAtoms) {
            if (atom.type === 'class') {
                const variable = atom.variable;
                this.variables.add(variable);
                
                if (!this.classes[variable]) {
                    this.classes[variable] = [];
                }
                
                this.classes[variable].push({
                    class: `${atom.prefix}:${atom.class}`,
                    part: atom.part
                });
            } else if (atom.type === 'property') {
                const subject = atom.subject;
                const object = atom.object;
                
                this.variables.add(subject);
                if (object.startsWith('?')) {
                    this.variables.add(object);
                }
                
                this.properties.push({
                    subject: subject,
                    predicate: `${atom.prefix}:${atom.property}`,
                    object: object,
                    part: atom.part
                });
            }
        }

        // Generate DOT
        return this.createDOTGraph();
    }

    /**
     * Create DOT graph representation
     * @returns {string} DOT graph string
     */
    createDOTGraph() {
        const lines = [];
        lines.push('digraph SWRL_Rule {');
        lines.push('    rankdir=LR;');
        lines.push('    node [shape=box, style=rounded];');
        lines.push('');

        // Collect all unique classes
        const allClasses = new Set();
        for (const variable in this.classes) {
            for (const clsInfo of this.classes[variable]) {
                allClasses.add(clsInfo.class);
            }
        }

        // Add class nodes
        lines.push('    // Classes');
        const sortedClasses = Array.from(allClasses).sort();
        for (const cls of sortedClasses) {
            lines.push(`    "${cls}" [shape=ellipse, fillcolor=lightgreen, style=filled];`);
        }
        lines.push('');

        // Add variables as nodes (without class labels)
        lines.push('    // Variables (Instances)');
        const sortedVariables = Array.from(this.variables).sort();
        for (const variable of sortedVariables) {
            lines.push(`    "${variable}" [label="${variable}", fillcolor=lightblue, style="rounded,filled"];`);
        }
        lines.push('');

        // Add literal nodes for non-variable objects
        lines.push('    // Literals');
        const literals = new Set();
        for (const prop of this.properties) {
            const obj = prop.object;
            if (!obj.startsWith('?')) {
                literals.add(obj);
            }
        }

        const sortedLiterals = Array.from(literals).sort();
        for (const literal of sortedLiterals) {
            lines.push(`    "${literal}" [shape=box, style=filled, fillcolor=lightyellow];`);
        }
        lines.push('');

        // Add class-to-instance edges (type relationships)
        lines.push('    // Class Assertions (rdf:type)');
        for (const variable of sortedVariables) {
            if (this.classes[variable]) {
                for (const clsInfo of this.classes[variable]) {
                    const cls = clsInfo.class;
                    const part = clsInfo.part;
                    
                    // Style edges differently for consequent
                    if (part === 'consequent') {
                        lines.push(`    "${cls}" -> "${variable}" [label="rdf:type", color=blue, penwidth=2, style=dashed];`);
                    } else {
                        lines.push(`    "${cls}" -> "${variable}" [label="rdf:type", style=dashed];`);
                    }
                }
            }
        }
        lines.push('');

        // Add properties as edges
        lines.push('    // Properties');
        for (const prop of this.properties) {
            const subject = prop.subject;
            const predicate = prop.predicate;
            const object = prop.object;
            const part = prop.part;

            // Style edges differently for consequent
            if (part === 'consequent') {
                lines.push(`    "${subject}" -> "${object}" [label="${predicate}", color=blue, penwidth=2];`);
            } else {
                lines.push(`    "${subject}" -> "${object}" [label="${predicate}"];`);
            }
        }

        lines.push('}');
        return lines.join('\n');
    }
}

// Make the class available globally
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SWRLToDOT;
}
