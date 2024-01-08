# course_db.py
# extract a course database from the CoS for dependencies / course info 
import fitz
import re
from img2table.ocr import TesseractOCR 
from img2table.document import PDF
import json
import copy
import sys

# 2023-24 CoS ONLY
COS = sys.argv[1]

# Hardcoded for the 2024 CoS
COURSE_DESCRIPTION_PAGE_FIRST = 178
COURSE_DESCRIPTION_PAGE_LAST = 417

PROGRAMME_PAGE_FIRST = 46
PROGRAMME_PAGE_LAST = 96

COURSE_PATTERN = r"^([A-Za-z]{3})\s*(\d{3})"
CREDIT_PATTERN = r"^\d"
PREREQ_PATTERN = r"^Pre-requi"
OVERLAP_PATTERN = r"^[Oo]verlaps"

STANDARD_COS_PAGE_X1 = 49
STANDARD_COS_PAGE_X2 = 300
STANDARD_COS_PAGE_X3 = 596
STANDARD_COS_PAGE_Y1 = 84
STANDARD_COS_PAGE_Y2 = 790

def extract_text_by_coordinates(pdf_document, page_number, x1, y1, x2, y2):
    page = pdf_document[page_number - 1]
    rect = fitz.Rect(x1, y1, x2, y2)
    
    selected_text = page.get_text("text", clip=rect)
    return selected_text

def standard_cos_page_scraper(pdf_doc, page):
    x1, y1 = STANDARD_COS_PAGE_X1, STANDARD_COS_PAGE_Y1  # Starting coordinates of the rectangle
    x2, y2 = STANDARD_COS_PAGE_X2, STANDARD_COS_PAGE_Y2  # Ending coordinates of the rectangle
    x3, y3 = STANDARD_COS_PAGE_X2, STANDARD_COS_PAGE_Y1
    x4, y4 = STANDARD_COS_PAGE_X3, STANDARD_COS_PAGE_Y2
    left_side = extract_text_by_coordinates(pdf_doc, page, x1, y1, x2, y2)
    right_side = extract_text_by_coordinates(pdf_doc, page, x3, y3, x4, y4)
    return [left_side, right_side]

def scrape_courses_description():
    scraped_dataset = []
    
    first_page_i = COURSE_DESCRIPTION_PAGE_FIRST
    last_page_i = COURSE_DESCRIPTION_PAGE_LAST

    pdf_doc = fitz.open(COS)
    for page in range(first_page_i, last_page_i + 1):
        scraped_dataset.extend(standard_cos_page_scraper(pdf_doc, page))

    pdf_doc.close()

    scraped_dataset = '\n'.join(scraped_dataset)
    scraped_dataset = list(map(lambda x: x.strip(), scraped_dataset.split('\n')))
    
    return scraped_dataset

def parse_course_description(text):

    re_course = r"^([A-Za-z]{3}\d{3})\s+(.+)"
    re_credits = r"^([0-9.]+)\s+[Cc]redits\s+\((\d+)-(\d+)-(\d+)\)"
    re_prereq = r"^[Pp]re-requisite.*"
    re_overlap = r"^[Oo]verlap.*"

    courses = []

    i = 0
    starter_template = {
        "code": None, # "APL100"
        "name": "",
        "prereqs": "", 
        "overlap": "",
        "credits": 0,
        "hours": {
            "lecture": 0,
            "tutorial": 0,
            "practical": 0
        },
        "description": ""
    }

    template = copy.deepcopy(starter_template)

    while i < len(text):
        if re.match(re_course, text[i]):
            if template["code"]:
                template['description'] = template['description'].strip()
                courses.append(template)
                template = copy.deepcopy(starter_template)
            groups = re.match(re_course, text[i])
            template['code'] = groups[1]
            template['name'] = groups[2]
        elif re.match(re_credits, text[i]):
            groups = re.match(re_credits, text[i])
            template['credits'] = float(groups[1])
            template['hours']['lecture'] = int(groups[2])
            template['hours']['tutorial'] = int(groups[3])
            template['hours']['practical'] = int(groups[4])
        elif re.match(re_prereq, text[i]): 
            # manually handle multiline prereqs
            prereqs = text[i].split(':', 1)[1].strip()
            template['prereqs'] = prereqs
        elif re.match(re_overlap, text[i]):
            overlaps = text[i].split(':', 1)[1].strip()
            template['overlap'] = overlaps
        else:
            template['description'] += ' ' + text[i]
        i += 1

    template['description'] = template['description'].strip()
    courses.append(template)

    return courses

def main():
    course_text = scrape_courses_description()
    parsed_courses = parse_course_description(course_text)

    with open(sys.argv[2], 'w') as outfile:
        json.dump(parsed_courses, outfile, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
