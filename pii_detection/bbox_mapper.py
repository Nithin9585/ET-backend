from typing import List
from .models import BBox

def get_subspan_bbox(span_bbox: BBox, span_text_length: int, entity_start: int, entity_end: int) -> BBox:
    if span_text_length <= 0:
        return span_bbox
    clamped_start = max(0, min(entity_start, span_text_length))
    clamped_end = max(clamped_start, min(entity_end, span_text_length))
    if clamped_end <= clamped_start:
        return span_bbox
    width = max(0.0, span_bbox.x2 - span_bbox.x1)
    start_ratio = clamped_start / float(span_text_length)
    end_ratio = clamped_end / float(span_text_length)
    x1 = span_bbox.x1 + width * start_ratio
    x2 = span_bbox.x1 + width * end_ratio
    return BBox(x1=x1, y1=span_bbox.y1, x2=x2, y2=span_bbox.y2)

def merge_bboxes(bboxes: List[BBox]) -> BBox:
    if not bboxes:
        return BBox(x1=0.0, y1=0.0, x2=0.0, y2=0.0)
    x1 = min(b.x1 for b in bboxes)
    y1 = min(b.y1 for b in bboxes)
    x2 = max(b.x2 for b in bboxes)
    y2 = max(b.y2 for b in bboxes)
    return BBox(x1=x1, y1=y1, x2=x2, y2=y2)

def clamp_bbox_to_page(bbox: BBox, page_width: float, page_height: float) -> BBox:
    x1 = max(0.0, min(bbox.x1, page_width))
    y1 = max(0.0, min(bbox.y1, page_height))
    x2 = max(0.0, min(bbox.x2, page_width))
    y2 = max(0.0, min(bbox.y2, page_height))
    if x2 < x1:
        x1, x2 = x2, x1
    if y2 < y1:
        y1, y2 = y2, y1
    return BBox(x1=x1, y1=y1, x2=x2, y2=y2)
