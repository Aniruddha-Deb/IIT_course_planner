# course_plans.py
# extract course plans given the COS PDF
import fitz
import re
from img2table.ocr import TesseractOCR 
from img2table.document import PDF
import json
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

def scrape_course_header(pdf_doc, page_i):
    X1, X2 = 49, 596
    Y1, Y2 = 0, 84
    return extract_text_by_coordinates(pdf_doc, page_i, X1, Y1, X2, Y2).split("\n")

def is_course_table_page(pdf_doc, page_i):
    X1, X2 = 526, 596
    Y1, Y2 = 60, 200
    extractedText = extract_text_by_coordinates(pdf_doc, page_i, X1, Y1, X2, Y2)
    return "total" in extractedText.lower()

def get_all_programme_details():
    FIRST_PAGE_I = PROGRAMME_PAGE_FIRST
    LAST_PAGE_I = PROGRAMME_PAGE_LAST
    ocr = TesseractOCR()

    pdf_doc = fitz.open(COS)
    all_courses = []
    curr_course = {
        "header" : "",
        "body" : []
    }
    re_course = r".*([A-Z]{3}\d{3}|DE|OC|HUL[23]XX).*"
    prev_table_page = True
    for page_i in range(FIRST_PAGE_I, LAST_PAGE_I + 1):
        if is_course_table_page(pdf_doc, page_i):
            temp = "\n".join(curr_course["body"])
            curr_course['body'] = list(map(lambda x : x.strip(), temp.split('\n')))

            pdf = PDF(COS, pages=[page_i-1], pdf_text_extraction=True, detect_rotation=False)
            tables = pdf.extract_tables(ocr=ocr, implicit_rows=False, borderless_tables=False, min_confidence=50)
            edf = tables[page_i-1][0].df

            recommended = []
            
            for col in [3,4,8,11,14,17,20,23]:
                courses = set()
                for course in edf.iloc[:,col]:
                    if not course:
                        continue
                    groups = re.match(re_course, course, re.DOTALL)
                    if groups:
                        course = groups[1]
                        courses.add(course)
                recommended.append(list(courses))

            # curr_course['recommended'] = recommended
            curr_course['recommended'] = recommended

            all_courses.append(curr_course)
            curr_course = {
                "header" : "",
                "body" : []
            }
            prev_table_page = True
            continue
        if prev_table_page:
            prev_table_page = False
            curr_course["header"] = scrape_course_header(pdf_doc, page_i)
        curr_course["body"] += standard_cos_page_scraper(pdf_doc, page_i)
    pdf_doc.close()
    print(len(all_courses))

    curr_course

    return all_courses

def parse_course(course):

    template = {
            "code": "CS1",
            "name": "B.Tech in Computer Science and Engineeering",
            "credits" : {
                "BS": 24,
                "EAS": 19,
                "HuSS": 15,
                "PL": 0,
                "DC": 0,
                "DE": 0,
                "OC": 0,
                "MTech" : {
                    "PC": 0,
                    "PE": 0,
                }
            },
            "courses": {
                "PL": [],
                "DC": [],
                "DE": [],
                "MTech": {
                    "PC": [],
                    "PE": []
                }
            },
            "recommended" : []
        }

    template['code'] = course['header'][0].split(' ')[-1]
    template['name'] = course['header'][1]
    if template['code'] == 'DD1':
        return template

    i = 0
    cbody = course['body']

    line_map = {
        'Programme-linked Courses': 'PL',
        'Departmental Core': 'DC',
        'Departmental Electives': 'DE',
        'Open Category Courses': 'OC'
    }
    
    while i < len(cbody) :
        for (l, c) in line_map.items():
            if cbody[i] == l and template['credits'][c] == 0:
                i += 1
                while i < len(cbody) and cbody[i] == '':
                    i += 1
                template['credits'][c] = float(cbody[i])

        i += 1

    assert template['credits']['PL'] > 0, f"Could not parse PL for code {template['code']}"
    assert template['credits']['DC'] > 0, f"Could not parse DC for code {template['code']}"
    assert template['credits']['DE'] > 0, f"Could not parse DE for code {template['code']}"
    assert template['credits']['OC'] > 0, f"Could not parse OC for code {template['code']}"

    course_map = {
        'Programme-Linked Basic / Engineering Arts / Sciences Core' : 'PL',
        'Departmental Core': 'DC',
        'Departmental Electives': 'DE'
        # TODO Mtech
    }

    i = 28
    while i < len(cbody):
        for (l, c) in course_map.items():
            if cbody[i] == l and not template['courses'][c]:
                while i < len(cbody)-1:
                    i += 1
                    if cbody[i] == '':
                        continue
                    if cbody[i] == "Total Credits":
                        break
                    groups = re.match(COURSE_PATTERN, cbody[i])
                    if groups:
                        template['courses'][c].append(groups[1]+groups[2])
        i += 1

    assert template['courses']['PL'] != [], f"Could not parse PL courses for code {template['code']}"
    assert template['courses']['DC'] != [], f"Could not parse DC courses for code {template['code']}"
    assert template['courses']['DE'] != [], f"Could not parse DE courses for code {template['code']}"

    template['recommended'] = course['recommended']
    
    return template

def parse_all_courses(all_courses):
    parsed_courses = {}
    for course in all_courses:
        p = parse_course(course)
        parsed_courses[p['code']] = p

    return parsed_courses
    
def main():
    all_courses = get_all_programme_details()
    parsed_courses = parse_all_courses(all_courses)

    with open(sys.argv[2], 'w') as outfile:
        json.dump(parsed_courses, outfile, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
