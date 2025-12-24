# SWRL Rule Visualizer

A web-based tool to visualize SWRL (Semantic Web Rule Language) rules as interactive graphs. Perfect for GitHub Pages deployment!

## 🚀 Features

- **Interactive Web Interface**: Clean, modern UI for inputting SWRL rules
- **Real-time Visualization**: Instantly converts rules to DOT format and renders graphs
- **Multiple Export Options**: Download as DOT or SVG files
- **Example Rules**: Pre-loaded examples to get started quickly
- **Color-coded Visualization**: 
  - Green ellipses for classes
  - Blue boxes for variables/instances
  - Yellow boxes for literals
  - Blue edges for consequent (inferred) relationships
  - Black edges for antecedent (given) relationships

## 📋 SWRL Rule Format

SWRL rules follow this structure:
```
Antecedent ^ Antecedent -> Consequent ^ Consequent
```

### Example:
```
bot:Building(?b) ^ bot:hasElement(?b, ?ew) ^ fisa:ExternalWall(?ew) -> fisa:FireWallAsExternalWall(?ew)
```

## 🌐 GitHub Pages Deployment

### Quick Setup:

1. **Clone or upload these files to your repository:**
   - `index.html`
   - `swrl-visualizer.js`
   - `README.md`

2. **Enable GitHub Pages:**
   - Go to your repository Settings
   - Navigate to "Pages" section
   - Under "Source", select your branch (usually `main` or `master`)
   - Click Save

3. **Access your site:**
   - Your visualizer will be available at: `https://yourusername.github.io/repository-name/`

### Alternative: Direct File Usage

You can also just open `index.html` directly in any modern web browser - no server required!

## 💻 Local Development

Simply open `index.html` in a web browser. No build process or dependencies needed!

## 🎯 Usage

1. Enter or paste your SWRL rule in the text area
2. Click "🚀 Convert to DOT" to generate the visualization
3. View the DOT code and graph visualization
4. Download as DOT or SVG if needed

## 📚 Example Rules Included

- Fire safety building regulations
- Fire compartment adjacency
- Space occupancy requirements

## 🛠️ Technology Stack

- **HTML5/CSS3**: Modern, responsive interface
- **JavaScript (ES6+)**: SWRL parsing and DOT generation
- **Viz.js**: Client-side DOT graph rendering
- **No backend required**: Runs entirely in the browser

## 📝 SWRL Atom Types Supported

### Class Atoms
```
prefix:ClassName(?variable)
```

### Property Atoms
```
prefix:propertyName(?subject, ?object)
prefix:propertyName(?subject, literal)
```

## 🎨 Customization

You can modify the visualization colors and styles in the `createDOTGraph()` method in `swrl-visualizer.js`:

- Classes: `fillcolor=lightgreen`
- Variables: `fillcolor=lightblue`
- Literals: `fillcolor=lightyellow`
- Consequent edges: `color=blue, penwidth=2`

## 🤝 Contributing

Feel free to fork, modify, and submit pull requests!

## 📄 License

Open source - use freely for your projects!

## 🔗 Related Resources

- [SWRL Specification](https://www.w3.org/Submission/SWRL/)
- [Graphviz DOT Language](https://graphviz.org/doc/info/lang.html)
- [Viz.js Documentation](https://github.com/mdaines/viz-js)

---

Made with ❤️ for the Semantic Web community
