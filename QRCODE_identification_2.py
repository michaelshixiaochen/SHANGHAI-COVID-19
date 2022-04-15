#需要安装opencv-python、opencv-contrib-python、json等库
import cv2
import os
import numpy as np
import json
import pandas as pd

def get_filelist(dir, Filelist):
    """
    遍历图片所在文件夹
    :param dir: 需要遍历的文件夹
    :param Filelist: 定义文件名列表，输入时一般为空
    :return Filelist: 返回文件名列表
    """
    newDir = dir
    if os.path.isfile(dir):
        Filelist.append(dir)
        # # 若只是要返回文件文，使用这个
        # Filelist.append(os.path.basename(dir))
    elif os.path.isdir(dir):
        for s in os.listdir(dir):
            # 如果需要忽略某些文件夹，使用以下代码
            # if s == "xxx":
            # continue
            newDir = os.path.join(dir, s)
            get_filelist(newDir, Filelist)
    return Filelist

def wechatcv(filename):
    """
    调用微信二维码识别
    :param filename: 需要识别的文件路径
    :return kangyuanshuju: 返回户号及抗原编码
    调用wechat_qrcode_WeChatQRCode过程中需加载detect.prototxt、detect.caffemodel、sr.prototxt、sr.caffemodel四个模型，该四个模型可在https://github.com/WeChatCV/opencv_3rdparty/tree/wechat_qrcode下载
    """
    kangyuanshuju={}
    detect_obj = cv2.wechat_qrcode_WeChatQRCode(r'\wechatcv\detect.prototxt',r'\wechatcv\detect.caffemodel',r'\wechatcv\sr.prototxt',r'\wechatcv\sr.caffemodel')
    img = cv2.imdecode(np.fromfile(filename, dtype=np.uint8),-1)
    res,points = detect_obj.detectAndDecode(img)    #res为识别结果，返回为字符串
    #print(filename[-10:-6]) #源程序读取的图片该4位为户号，此处可根据实际情况进行调整
    #print('res:',res)
    kangyuanshuju['户名']=filename[-10:-6]
    kangyuanshuju['抗原编码']=res
    #print('points:',points)

    '''
    #该段程序用于作图并定位二维码
    for pos in points:
        color = (0, 0, 255)
        thick = 3
        for p in [(0, 1), (1, 2), (2, 3), (3, 0)]:
            start = int(pos[p[0]][0]), int(pos[p[0]][1])
            end = int(pos[p[1]][0]), int(pos[p[1]][1])
            cv2.line(img, start, end, color, thick)

    cv2.imshow('img', img)
    cv2.imwrite('wechat-qrcode-detect-1.jpg', img)
    cv2.waitKey()
    cv2.destroyAllWindows()
    '''
    return kangyuanshuju


def export_excel(dic_data,excelname):
    # 将字典列表转换为DataFrame
    pf=pd.DataFrame(list(dic_data))
    # 指定字段顺序
    order=['户名', '抗原编码']
    pf=pf[order]
    # 将列名替换为中文
    columns_map={
        '户名': '户名',
        '抗原编码': '抗原编码',
    }
    pf.rename(columns=columns_map, inplace=True)
    # 指定生成的Excel表格名称
    file_path=pd.ExcelWriter(excelname+'.xlsx')
    # file_csv_path = pd.read_csv("compound.csv")
    # 替换空单元格
    pf.fillna(' ', inplace=True)
    # 输出
    pf.to_excel(file_path, encoding='utf-8', index=False)
    # pf.to_csv(file_csv_path, encoding='utf-8', index=False)
    # 保存表格
    file_path.save()

if __name__ == '__main__':

    kangyuanshuju=[]                  #定义抗原编码数据为字典
    dir = input('请输入图片路径：')        #获得抗原图片路径
    excelname=input('请输入输出的excel文件名')
    Filelist=get_filelist(dir,[])       #遍历文件夹获得所有图片名称
    #print(len(Filelist))
    for filename in Filelist:
        kangyuan=wechatcv(filename)     #调用二维码识别函数
        kangyuanshuju.append(kangyuan)
        #kangyuanshuju.update(kangyuan)  #更新抗原编码字典
    kangyuanshuju_sorted=json.dumps(kangyuanshuju, indent=4, ensure_ascii=False, sort_keys=True, separators=(',', ':'))    #格式化字典
    print(kangyuanshuju_sorted)
    export_excel(kangyuanshuju,excelname)
    input("Press <enter>")




