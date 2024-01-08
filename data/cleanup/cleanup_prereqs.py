from mistral import load_model, generate
import argparse
import json

prompt = """You need to parse a set of course prerequisites into logical expressions which can be parsed by a machine. The input format is in plaintext, and the output is a boolean expression within square brackets. If there is any confusion, choose the most unambiguous combination. Ignore "Or Equivalent", "Undergraduate" or any other qualifiers. ONLY include alphanumeric course codes, or EC values. EXACTLY FOLLOW THE FORMAT.

Prerequisites: APL104/APL105/APL108 EC50
Parsed: [(APL104 || APL105 || APL108) && EC50]

Prerequisites: APL106 or equivalent, APL321
Parsed: [APL106 && APL321]

Prerequisites: BBL131, BBL331 or Masters’ degree in
Parsed: [BBL131 && BBL331]

Prerequisites: CVL242 or Concurrent with CVL242
Parsed: [CVL242 || CVL242c]

Prerequisites: CVL281 and CVL282
Parsed: [CVL281 && CVL282]

Prerequisites: CVL282 or EC 75
Parsed: [CVL282 || EC75]

Prerequisites: To be declared by Instructor
Parsed: []

Prerequisites: CLL222, CLL352
Parsed: [CLL252 && CLL352]

Prerequisites: M.Tech: Nil; B.Tech: Instructor's permission
Parsed: []

Prerequisites: MCL140, APL106 or APL105, ESL200, ESL262,
Parsed: [MCL140 && (APL106 || APL105) && ESL200 && ESL262]

Prerequisites: %s
Parsed:"""

def parse_llm_output(output):
    s = output.strip()
    print(s)
    return s

def main():
    parser = argparse.ArgumentParser(description="Cleanup prerequisites")
    parser.add_argument(
        "-m",
        "--model-path",
        type=str,
        default=None,
        help="The path to the model weights and tokenizer",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        default=None,
        help="input courses.json file",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="courses_fmtd.json",
        help="cleaned up output file",
    )

    args = parser.parse_args()

    if not args.model_path:
        print("[ERROR] Model path is required to run script")
        return
    if not args.input:
        print("[ERROR] Input file is required to clean up prerequisites")
        return

    model, tokenizer = load_model(args.model_path)
    courses = json.load(open(args.input, 'r'))

    for course in courses:
        llm_output = generate(prompt % course['prereqs'], model, tokenizer, break_tok=13) # \n
        course['prereqs'] = parse_llm_output(llm_output)

    json.dump(courses, open(args.output, 'w'), ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
