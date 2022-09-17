class SortBoxes(object):
    def __init__(self, result_PPStructure):
        self.results = []
        self.__sort__(result_PPStructure)

    def __sort__(self, result):
        '''從上到下左到右排序'''
        results = []
        for region in result:
            if region['res']['boxes'] is None:
                continue
            
            result_len = len(region['res']['boxes'])
            for i in range(result_len):
                ocrResult = OcrResult()
                bbox = region['res']['boxes'][i]
                ocrResult.boxes = [bbox[0], bbox[1], bbox[2], bbox[1], bbox[2], bbox[3], bbox[0], bbox[3]]
                ocrResult.text = region['res']['rec_res'][i][0]
                ocrResult.score = region['res']['rec_res'][i][1]
                results.append(ocrResult)

        results = sorted(results, key = lambda x : (x.boxes[1], x.boxes[0]))

        tmpRow = []
        for i in range(0, len(results)):
            if tmpRow:
                if (results[i].boxes[1] - tmpRow[-1].boxes[1] < max(results[i].boxes[5] - results[i].boxes[1], tmpRow[-1].boxes[5] - tmpRow[-1].boxes[1]) / 2):
                    tmpRow.append(results[i])
                else:
                    self.results.extend(sorted(tmpRow, key = lambda x : (x.boxes[0])))
                    tmpRow = []
                    tmpRow.append(results[i])
            else:
                tmpRow.append(results[i])
        
        if tmpRow:
            self.results.extend(sorted(tmpRow, key = lambda x : (x.boxes[0])))
        
class OcrResult(object):
    def __init__(self):
        self.boxes = []
        self.text = ""
        self.score = 0

import os
import cv2
from paddleocr import PPStructure,save_structure_res,draw_ocr
from PIL import Image

if __name__ == '__main__':
    dirname = os.path.dirname(__file__)
    table_engine = PPStructure(use_pdserving=False,
                                        use_gpu=True,
                                        lang='en',
                                        layout=False,
                                        show_log=False,structure_version='PP-Structure')

    img_path = os.path.join(dirname, 'Image/21207.jpg')
    img = cv2.imread(img_path)
    result = table_engine(img, return_ocr_result_in_table=True)

    sortBoxes = SortBoxes(result)

    # # draw result
    image = Image.open(img_path).convert('RGB')
    boxes = [ x.boxes for x in sortBoxes.results]
    txts = [ x.text for x in sortBoxes.results]
    scores = [ x.score for x in sortBoxes.results]
    im_show = draw_ocr(image, boxes, txts, scores, font_path = os.path.join(dirname, 'Font/SourceHanSansHW-VF.ttf'), drop_score=0.05)
    im_show = Image.fromarray(im_show)
    im_show.show()

