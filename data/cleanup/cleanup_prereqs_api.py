import argparse
import re
import openai
import os
import json
from dotenv import load_dotenv
from multiprocessing import Pool

load_dotenv()

prompt = """Prereqs: APL104/APL105/APL108 EC50
Parsed: [(APL104 || APL105 || APL108) && EC50]

Prereqs: APL106 or equivalent, APL321
Parsed: [APL106 && APL321]

Prereqs: BBL131, BBL331 or Masters’ degree in
Parsed: [BBL131 && BBL331]

Prereqs: CVL242 or Concurrent with CVL242
Parsed: [CVL242 || CVL242c]

Prereqs: CVL282 or EC 75
Parsed: [CVL282 || EC75]

Prereqs: To be declared by Instructor
Parsed: []

Prereqs: For uG: AML140 and MCL111; For Non-ME
Parsed: [AML140 && MCL111]

Prereqs: TXL111/TXL221 for uG students
Parsed: [TXL111 || TXL221]

Prereqs: Any one of ELL 409/ELL 774 / COL 341/ COL
Parsed: [ELL409 || ELL774 || COL341]

Prereqs: M.Tech: Nil; B.Tech: Instructor's permission
Parsed: []

Prereqs: MCL140, APL106 or APL105, ESL200, ESL262,
Parsed: [MCL140 && (APL106 || APL105) && ESL200 && ESL262]

Prereqs: %s
Parsed:"""

client = openai.OpenAI(
  api_key = os.getenv("TOGETHER_API_KEY"),
  base_url = 'https://api.together.xyz',
)

def generate(prompt):

    chat_completion = client.chat.completions.create(
      messages=[
        {
          "role": "system",
          "content": "You need to parse a set of course prerequisites into logical expressions which can be parsed by a machine. The input format is in plaintext, and the output is a boolean expression within square brackets. Ignore text or any trailing characters which are not course codes. ONLY include alphanumeric course codes, or EC values. If there is any ambiguity, output []. Make sure you EXACTLY FOLLOW THE FORMAT.",
        },
        {
          "role": "user",
          "content": prompt,
        }
      ],
      model="mistralai/Mistral-7B-Instruct-v0.2",
      max_tokens=512,
      temperature=0,
      stop=["\n"]
    )

    return chat_completion.choices[0].message.content

def parse_llm_output(output):
    s = output.strip()
    expr = re.search(r'\[(.*)\]', s, re.IGNORECASE)
    if expr:
        return expr.group(1)
    else:
        return ""

def process_course(course):
    llm_output = generate(prompt % course['prereqs'])
    course['prereqs'] = parse_llm_output(llm_output)
    print(course['prereqs'])
    return course

def main():
    parser = argparse.ArgumentParser(description="Cleanup prerequisites")
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

    if not args.input:
        print("[ERROR] Input file is required to clean up prerequisites")
        return

    courses = json.load(open(args.input, 'r'))

    courses = list(map(process_course, courses))

    json.dump(courses, open(args.output, 'w'), ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
