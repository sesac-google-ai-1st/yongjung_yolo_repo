import numpy as np
import os
from lxml import etree
from glob import glob

# image 파일 내 box들의 label 3가지 종류
CLASSES = ["car", "bus", "truck"]

# 박스의 중심점, 가로 길이, 세로 길이 계산해서 변환
def to_yolov8(y):
  """
  # change to yolo v8 format
  # [x_top_left, y_top_left, x_bottom_right, y_bottom_right] to
  # [x_center, y_center, width, height]
  """
  width = y[2] - y[0]
  height = y[3] - y[1]

  if width < 0 or height < 0:
      print("ERROR: negative width or height ", width, height, y)
      raise AssertionError("Negative width or height")
        
  return (y[0] + (width/2)), (y[1] + (height/2)), width, height

# xml 파일 내용 쪼개서 지저분하게 반복되는 키 값들은 빼주고 value들만 모으기
def load_xml_annotations(f):
  tree = etree.parse(f)
  anns = []
  for dim in tree.xpath("image"):
    image_filename = dim.attrib["name"]
    width = int(dim.attrib["width"])
    height = int(dim.attrib["height"])
    # print(image_filename)
    # print(len(dim.xpath("box")))
    boxes = []
    for box in dim.xpath("box"):
      label = CLASSES.index(box.attrib["label"])
      xtl, ytl = box.attrib["xtl"], box.attrib["ytl"]
      xbr, ybr = box.attrib["xbr"], box.attrib["ybr"]

      xc, yc, w, h = to_yolov8([float(xtl), float(ytl), float(xbr), float(ybr)])  ## 박스의 중심점, 가로 길이, 세로 길이 계산해서 변환
      boxes.append([label, round(xc/width, 5), round(yc/height, 5), round(w/width, 5), round(h/height, 5)])  # 변환한 걸 그대로 리턴하지 않고 가로 길이, 세로 길이로 나눠서 스케일링 해준 값을 리턴.

    anns.append([image_filename, width, height, boxes])

  return np.array(anns, dtype = 'object')

# xml파일 하나에 해당하는 폴더 하나 생성, 그 안에 이미지 하나 당 txt 파일 하나 생성
def write_yolov8_txt(folder, annotation):
  out_filename = str(folder + annotation[0][:-3])
  out_filename = os.path.splitext(out_filename)[0] + '.txt'

  f = open(out_filename,"w+")
  for box in annotation[3]:
    f.write("{} {} {} {} {}\n".format(box[0], box[1], box[2], box[3], box[4]))



# 전체 파일 돌리기
HOME = os.getcwd()
# dataPath = '{}/dataset/highway_total/valid/label'.format(HOME)
dataPath = '{}/dataset/highway_total/train/label'.format(HOME)
for filename in glob(os.path.join(dataPath, '*.xml')):
  anns = load_xml_annotations(filename)
  basename = os.path.basename(filename)
  folder = os.path.join(dataPath, os.path.splitext(basename)[0])
  os.makedirs(folder, exist_ok=True)
  for ann in anns:
    write_yolov8_txt(folder + '/', ann)


# # 예시로 파일 하나만 잡고 실제 객체 생성
# HOME = os.getcwd()
# dataPath = '{}/highway/valid/label'.format(HOME)
# fileName = 'Suwon_CH01_20200720_1830_MON_9m_RH_highway_TW5_sunny_FHD.xml'
# folderName = os.path.splitext(fileName)[0]

# label_file = os.path.join(dataPath, fileName)
# print(label_file)

# basename = os.path.basename(label_file)
# folder = os.path.join(dataPath, os.path.splitext(basename)[0])
# print(folder)

# anns = load_xml_annotations(label_file)

# os.makedirs(folder, exist_ok=True)

# for ann in anns:
#   write_yolov8_txt(folder + '/', ann)