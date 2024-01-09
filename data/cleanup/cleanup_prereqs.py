from mistral import Mistral, Tokenizer, load_model
import mlx.core as mx
from typing import Optional
import argparse
import json

preprompt = """You need to parse a set of course prerequisites into logical expressions which can be parsed by a machine. The input format is in plaintext, and the output is a boolean expression within square brackets. If there is any confusion, choose the most unambiguous combination. Ignore "Or Equivalent", "Undergraduate" or any other qualifiers. ONLY include alphanumeric course codes, or EC values. EXACTLY FOLLOW THE FORMAT.

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

Prerequisites: """

prompt = """%s
Parsed:"""

def sample(logits, temp):
    if temp == 0:
        return mx.argmax(logits, axis=-1)
    else:
        return mx.random.categorical(logits * (1 / temp))

def next_token(prompt: mx.array, model: Mistral, cache: Optional[mx.array] = None, temp: float = 0.0):

    if cache:
        logits, cache = model(prompt[None], cache)
    else:
        logits, cache = model(prompt[None])

    y = sample(logits[:, -1, :], temp)
    yield y

    while True:
        logits, cache = model(y[:, None], cache)
        y = sample(logits.squeeze(1), temp)
        yield y

def generate(prompts: list[str], model: Mistral, tokenizer: Tokenizer, cache: Optional[mx.array] = None,
             temp: float = 0.0, limit: int = 512,
             break_tok: Optional[int] = None):
    prompt = mx.array(tokenizer.batch_encode(prompt))
    tokens = []
    for token, ntoks in zip(next_token(prompt, model, cache, temp), range(limit)):
        tokens.append(token)
        if ntoks == 0:
            mx.eval(tokens)
        if break_tok and token == break_tok:
            break

    mx.eval(tokens)
    s = tokenizer.decode([t.item() for t in tokens])

    return(s)

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

    preprompt_toks = mx.array(tokenizer.encode(preprompt))
    logits, cache = model(preprompt_toks[None])

    for course in courses:
        llm_output = generate(prompt % course['prereqs'], model, tokenizer, cache, break_tok=13) # \n
        course['prereqs'] = parse_llm_output(llm_output)

    json.dump(courses, open(args.output, 'w'), ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
