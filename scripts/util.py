import fitz

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
