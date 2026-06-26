import os
import json

def generate_app(schema, output_dir="/home/aarush/Documents/vscode/temp/generated_app"):
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(f"{output_dir}/templates", exist_ok=True)
    
    generate_models(schema["db_schema"], output_dir)
    generate_routes(schema["api_schema"], schema["auth_schema"], output_dir)
    generate_templates(schema["ui_schema"], schema["db_schema"], output_dir)
    generate_main(output_dir)
    generate_requirements(output_dir)
    
    return output_dir

def generate_models(db_schema, output_dir):
    # Type mapping from our schema types to SQLAlchemy types
    type_map = {
        "integer": "db.Integer",
        "string": "db.String(255)",
        "boolean": "db.Boolean",
        "float": "db.Float",
        "number": "db.Float",
        "date": "db.DateTime",
        "text": "db.Text"
    }
    
    lines = []
    lines.append("from flask_sqlalchemy import SQLAlchemy")
    lines.append("")
    lines.append("db = SQLAlchemy()")
    lines.append("")
    
    for table in db_schema["tables"]:
        class_name = table["name"].capitalize()
        lines.append(f"class {class_name}(db.Model):")
        lines.append(f"    __tablename__ = '{table['name']}'")
        lines.append("")
        
        for col in table["columns"]:
            sql_type = type_map.get(col["type"], "db.String(255)")
            nullable = "False" if not col["nullable"] else "True"
            
            if col["name"] == "id":
                lines.append(f"    {col['name']} = db.Column({sql_type}, primary_key=True)")
            else:
                lines.append(f"    {col['name']} = db.Column({sql_type}, nullable={nullable})")
        
        lines.append("")
        lines.append("    def to_dict(self):")
        lines.append("        return {c.name: getattr(self, c.name) for c in self.__table__.columns}")
        lines.append("")
    
    with open(f"{output_dir}/models.py", "w") as f:
        f.write("\n".join(lines))

def generate_routes(api_schema, auth_schema, output_dir):
    lines = []
    lines.append("from flask import Blueprint, request, jsonify, session")
    lines.append("from models import db")
    lines.append("from functools import wraps")
    lines.append("")
    lines.append("api = Blueprint('api', __name__)")
    lines.append("")
    
    # Auth decorator
    lines.append("def login_required(f):")
    lines.append("    @wraps(f)")
    lines.append("    def decorated(*args, **kwargs):")
    lines.append("        if 'user_id' not in session:")
    lines.append("            return jsonify({'error': 'Unauthorized'}), 401")
    lines.append("        return f(*args, **kwargs)")
    lines.append("    return decorated")
    lines.append("")
    
    for endpoint in api_schema["endpoints"]:
        method = endpoint["method"]
        path = endpoint["path"]
        auth = endpoint["auth"]
        
        # Convert path to valid function name
        func_name = path.replace("/", "_").replace("-", "_").strip("_")
        func_name = f"{method.lower()}_{func_name}"
        
        lines.append(f"@api.route('{path}', methods=['{method}'])")
        if auth:
            lines.append("@login_required")
        lines.append(f"def {func_name}():")
        
        if method == "POST":
            lines.append("    data = request.get_json()")
        
        lines.append("    # TODO: implement logic")
        lines.append("    return jsonify({'message': 'success'}), 200")
        lines.append("")
    
    with open(f"{output_dir}/routes.py", "w") as f:
        f.write("\n".join(lines))

def generate_templates(ui_schema, db_schema, output_dir):
    # Group components by page
    pages = {}
    for component in ui_schema["components"]:
        page = component["page"]
        if page not in pages:
            pages[page] = []
        pages[page].append(component)
    
    # Generate base template
    base_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}App{% endblock %}</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: sans-serif; background: #f5f5f5; padding: 2rem; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; }
        input, button, select { padding: 0.5rem 1rem; margin: 0.25rem 0; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #333; color: white; cursor: pointer; border: none; }
        table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
        th, td { padding: 0.75rem; border-bottom: 1px solid #eee; text-align: left; }
        nav a { margin-right: 1rem; text-decoration: none; color: #333; }
    </style>
</head>
<body>
<div class="container">
    <nav>{% block nav %}{% endblock %}</nav>
    {% block content %}{% endblock %}
</div>
</body>
</html>"""
    
    with open(f"{output_dir}/templates/base.html", "w") as f:
        f.write(base_html)
    
    # Generate page templates
    for page_name, components in pages.items():
        html_lines = []
        html_lines.append("{% extends 'base.html' %}")
        html_lines.append(f"{{% block title %}}{page_name}{{% endblock %}}")
        html_lines.append("{% block content %}")
        html_lines.append(f"<h1>{page_name}</h1>")
        
        for component in components:
            comp_type = component["type"]
            props = component.get("props", {})
            
            if comp_type == "input":
                placeholder = props.get("placeholder", "")
                input_type = props.get("type", "text")
                html_lines.append(f'<input type="{input_type}" placeholder="{placeholder}" id="{component["id"]}">')
            
            elif comp_type == "button":
                text = props.get("text", "Submit")
                html_lines.append(f'<button id="{component["id"]}">{text}</button>')
            
            elif comp_type == "form":
                html_lines.append('<form>')
                fields = props.get("fields", []) or list(props.keys())
                for field in fields:
                    html_lines.append(f'<input type="text" name="{field}" placeholder="{field}"><br>')
                html_lines.append('<button type="submit">Submit</button>')
                html_lines.append('</form>')
            
            elif comp_type in ["list", "table"]:
                columns = props.get("columns", props.get("items", ["id", "name"]))
                html_lines.append('<table>')
                html_lines.append('<thead><tr>')
                for col in columns:
                    html_lines.append(f'<th>{col}</th>')
                html_lines.append('</tr></thead>')
                html_lines.append('<tbody id="' + component["id"] + '"></tbody>')
                html_lines.append('</table>')
        
        html_lines.append("{% endblock %}")
        
        filename = page_name.lower().replace(" ", "_") + ".html"
        with open(f"{output_dir}/templates/{filename}", "w") as f:
            f.write("\n".join(html_lines))

def generate_main(output_dir):
    main_code = """from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db
from routes import api

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SECRET_KEY'] = 'change-this-in-production'

db.init_app(app)

app.register_blueprint(api)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
"""
    with open(f"{output_dir}/main.py", "w") as f:
        f.write(main_code)

def generate_requirements(output_dir):
    reqs = """flask
flask-sqlalchemy
flask-cors
"""
    with open(f"{output_dir}/requirements.txt", "w") as f:
        f.write(reqs)

if __name__ == "__main__":
    with open("sample_schema.json", "r") as f:
        schema = json.load(f)
    
    output = generate_app(schema)
    print(f"App generated in: {output}")