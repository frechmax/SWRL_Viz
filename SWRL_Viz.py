import re
from typing import Dict, List, Tuple, Set

class SWRLToDOT:
    """Convert SWRL rules to DOT graph format"""
    
    def __init__(self):
        self.variables = set()
        self.classes = {}  # variable -> class
        self.properties = []  # (subject, predicate, object)
        self.atoms = []
        
    def parse_swrl_rule(self, rule: str) -> Tuple[List[str], List[str]]:
        """Parse SWRL rule into antecedent and consequent atoms"""
        # Split by arrow
        parts = rule.split('->')
        if len(parts) != 2:
            raise ValueError("Invalid SWRL rule: missing '->' separator")
        
        antecedent = parts[0].strip()
        consequent = parts[1].strip()
        
        # Parse atoms (separated by ^)
        antecedent_atoms = [atom.strip() for atom in re.split(r'\s*\^\s*', antecedent)]
        consequent_atoms = [atom.strip() for atom in re.split(r'\s*\^\s*', consequent)]
        
        return antecedent_atoms, consequent_atoms
    
    def parse_atom(self, atom: str) -> Dict:
        """Parse a single SWRL atom"""
        # Pattern for class atoms: prefix:ClassName(?var)
        class_pattern = r'(\w+):(\w+)\((\?\w+)\)'
        # Pattern for property atoms: prefix:propertyName(?var1, ?var2) or (?var1, literal)
        property_pattern = r'(\w+):(\w+)\((\?\w+),\s*(.+?)\)'
        
        class_match = re.match(class_pattern, atom)
        if class_match:
            prefix, class_name, variable = class_match.groups()
            return {
                'type': 'class',
                'prefix': prefix,
                'class': class_name,
                'variable': variable
            }
        
        property_match = re.match(property_pattern, atom)
        if property_match:
            prefix, property_name, subject, obj = property_match.groups()
            obj = obj.strip()
            return {
                'type': 'property',
                'prefix': prefix,
                'property': property_name,
                'subject': subject,
                'object': obj
            }
        
        raise ValueError(f"Cannot parse atom: {atom}")
    
    def generate_dot(self, rule: str, output_file: str = None) -> str:
        """Generate DOT graph from SWRL rule"""
        # Reset state
        self.variables = set()
        self.classes = {}
        self.properties = []
        
        # Parse rule
        antecedent_atoms, consequent_atoms = self.parse_swrl_rule(rule)
        
        # Process all atoms
        all_atoms = []
        for atom in antecedent_atoms:
            parsed = self.parse_atom(atom)
            parsed['part'] = 'antecedent'
            all_atoms.append(parsed)
            
        for atom in consequent_atoms:
            parsed = self.parse_atom(atom)
            parsed['part'] = 'consequent'
            all_atoms.append(parsed)
        
        # Extract variables, classes, and properties
        for atom in all_atoms:
            if atom['type'] == 'class':
                var = atom['variable']
                self.variables.add(var)
                if var not in self.classes:
                    self.classes[var] = []
                self.classes[var].append({
                    'class': f"{atom['prefix']}:{atom['class']}",
                    'part': atom['part']
                })
            elif atom['type'] == 'property':
                subject = atom['subject']
                obj = atom['object']
                self.variables.add(subject)
                if obj.startswith('?'):
                    self.variables.add(obj)
                self.properties.append({
                    'subject': subject,
                    'predicate': f"{atom['prefix']}:{atom['property']}",
                    'object': obj,
                    'part': atom['part']
                })
        
        # Generate DOT
        dot = self._create_dot_graph()
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(dot)
            print(f"DOT file saved to: {output_file}")
        
        return dot
    
    def _create_dot_graph(self) -> str:
        """Create DOT graph representation"""
        lines = []
        lines.append('digraph SWRL_Rule {')
        # lines.append('    rankdir=TD;')
        lines.append('    rankdir=LR;')
        lines.append('    node [shape=box, style=rounded];')
        lines.append('')
        
        # Collect all unique classes
        all_classes = set()
        for var, class_list in self.classes.items():
            for cls_info in class_list:
                all_classes.add(cls_info['class'])
        
        # Add class nodes
        lines.append('    // Classes')
        for cls in sorted(all_classes):
            lines.append(f'    "{cls}" [shape=ellipse, fillcolor=lightgreen, style=filled];')
        
        lines.append('')
        
        # Add variables as nodes (without class labels)
        lines.append('    // Variables (Instances)')
        for var in sorted(self.variables):
            lines.append(f'    "{var}" [label="{var}", fillcolor=lightblue, style="rounded,filled"];')
        
        lines.append('')
        
        # Add literal nodes for non-variable objects
        lines.append('    // Literals')
        literals = set()
        for prop in self.properties:
            obj = prop['object']
            if not obj.startswith('?'):
                literals.add(obj)
        
        for literal in sorted(literals):
            lines.append(f'    "{literal}" [shape=box, style=filled, fillcolor=lightyellow];')
        
        lines.append('')
        
        # Add class-to-instance edges (type relationships)
        lines.append('    // Class Assertions (rdf:type)')
        for var in sorted(self.variables):
            if var in self.classes:
                for cls_info in self.classes[var]:
                    cls = cls_info['class']
                    part = cls_info['part']
                    # Style edges differently for consequent
                    if part == 'consequent':
                        lines.append(f'    "{cls}" -> "{var}" [label="rdf:type", color=blue, penwidth=2, style=dashed];')
                    else:
                        lines.append(f'    "{cls}" -> "{var}" [label="rdf:type", style=dashed];')
        
        lines.append('')
        
        # Add properties as edges
        lines.append('    // Properties')
        for prop in self.properties:
            subject = prop['subject']
            predicate = prop['predicate']
            obj = prop['object']
            part = prop['part']
            
            # Style edges differently for consequent
            if part == 'consequent':
                lines.append(f'    "{subject}" -> "{obj}" [label="{predicate}", color=blue, penwidth=2];')
            else:
                lines.append(f'    "{subject}" -> "{obj}" [label="{predicate}"];')
        
        lines.append('}')
        
        return '\n'.join(lines)
    

swrl_rule = """bot:Building(?b) ^ bot:hasElement(?b, ?ew) ^ fisa:ExternalWall(?ew) ^ fisa:hasDistanceToBoundary(?ew, 0.0) -> fisa:FireWallAsExternalWall(?ew) ^ fisa:hasRequirementOfFireResistance(?ew, fisa:feuerbeständig) ^ fisa:hasRequirementOfFireBehaviour(?ew, fisa:nichtbrennbar) ^ fisa:hasAssessmentBasis(?ew, fisa:MBO_P30_A2_N1_A)"""

# Create converter
converter = SWRLToDOT()

# Generate DOT file
dot_content = converter.generate_dot(swrl_rule, output_file='swrl_rule_graph.dot')

# Display the DOT content
print("Generated DOT Graph:")
print("="*60)
print(dot_content)



try:
    import graphviz
    from IPython.display import display
    
    # Create graph from DOT source
    graph = graphviz.Source(dot_content)
    
    # Render to PDF file for external use
    graph.render('swrl_rule_graph', format='pdf', cleanup=True)
    print("Graph rendered to swrl_rule_graph.pdf")
    print("="*60)
    
    # Display in notebook as SVG (inline visualization)
    print("Graph visualization:")
    display(graph)
    
except ImportError:
    print("Graphviz not installed. Install with: pip install graphviz")


def swrl_to_dot(swrl_rule: str, output_file: str = 'output.dot') -> str:
    """
    Convert a SWRL rule to DOT format and save to file.
    
    Parameters:
    -----------
    swrl_rule : str
        The SWRL rule string
    output_file : str
        Output file path for the DOT file (default: 'output.dot')
    
    Returns:
    --------
    str : The DOT graph content
    
    Example:
    --------
    rule = "fisa:FireCompartment(?c1) ^ bot:adjacentZone(?c1, ?c2) -> fisa:InternalWall(?w)"
    dot = swrl_to_dot(rule, 'my_rule.dot')
    """
    converter = SWRLToDOT()
    return converter.generate_dot(swrl_rule, output_file)

# Test with your custom rule
print("Ready to convert SWRL rules to DOT format!")
print("Use: swrl_to_dot(your_rule, 'output.dot')")

def swrl_to_pdf(swrl_rule: str, output_pdf: str = 'output.pdf') -> None:
    """
    Convert a SWRL rule to a PDF graph using DOT format.
    
    Parameters:
    -----------
    swrl_rule : str
        The SWRL rule string
    output_pdf : str
        Output file path for the PDF file (default: 'output.pdf')
    
    Example:
    --------
    rule = "fisa:FireCompartment(?c1) ^ bot:adjacentZone(?c1, ?c2) -> fisa:InternalWall(?w)"
    swrl_to_pdf(rule, 'my_rule.pdf')
    """
    dot_content = swrl_to_dot(swrl_rule, output_file=None)
    
    try:
        import graphviz
        
        # Create graph from DOT source
        graph = graphviz.Source(dot_content)
        
        # Render to PDF file
        graph.render(output_pdf.replace('.pdf', ''), format='pdf', cleanup=True)
        print(f"Graph rendered to {output_pdf}")

        display(graph)
        
    except ImportError:
        print("Graphviz not installed. Install with: pip install graphviz")