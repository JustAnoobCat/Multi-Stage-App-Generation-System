import os
import json
from stage1_intent import extract_intent
from stage2_design import generate_design
from stage3_schema import generate_schema
from stage4_validator import validate_repair
from stage5_generator import generate_app

def run_pipeline(user_prompt):
    print("\nStage 1: Extracting Intent\n")
    intent = extract_intent(user_prompt)
    print(json.dumps(intent,indent=2))

    print("\nStage 2: Generating System Design\n")
    design = generate_design(intent)
    print(json.dumps(design,indent=2))

    print("\nStage 3: Generating Schema\n")
    schema = generate_schema(intent, design)
    print(json.dumps(schema,indent=2))

    print("\nStage 4: Validating and Repairing\n")
    final_schema, validation = validate_repair(intent, schema)

    print("\nValidation Results: ")
    for r in validation:
        status = "PASS" if r["passed"] else "FIXED"
        fix = f" → {r['fix']}" if r["fix"] else ""
        print(f"  [{status}] {r['check']}{fix}")

    print("\nStage 5: Generating App\n")
    output_dir = generate_app(final_schema)
    
    generated_files = []
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            filepath = os.path.join(root, file)
            generated_files.append(filepath.replace(output_dir + "/", ""))
    
    print(f"Generated {len(generated_files)} files in: {output_dir}")
    
    return final_schema, validation, generated_files

if __name__ == "__main__":
    """
    user_prompt = "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."
    
    final_schema, validation = run_pipeline(user_prompt)
    
    print("\n--- Final Schema ---")
    print(json.dumps(final_schema, indent=2))
    """

    final_schema, validation = run_pipeline("Build a CRM with login, contacts, dashboard, role-based access, and payments")

    with open("sample_schema.json", "w") as f:
        json.dump(final_schema, f, indent=2)

    print("Schema saved to sample_schema.json")