import io
import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Union, Optional


class FaceDetector:
    def __init__(
        self,
        face_cc: Union[cv2.CascadeClassifier, Path, str],
        face_cc_args: Optional[dict] = None,
        clahe: Optional[cv2.CLAHE] = None,
    ):
        self.clahe = clahe or cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        self.face_cc_args = face_cc_args or dict(
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(80, 80),
            flags=cv2.CASCADE_SCALE_IMAGE | cv2.CASCADE_DO_ROUGH_SEARCH
        )
        if isinstance(face_cc, (str, Path)):
            face_cc = cv2.CascadeClassifier(str(face_cc))
        self.face_cc = face_cc

    @staticmethod
    def imread(fp: Union[io.BufferedIOBase, Path, str]):
        if isinstance(fp, (str, Path)):
            return cv2.imread(str(fp), cv2.IMREAD_UNCHANGED)
        else:
            data = fp.read()
            np_data = np.frombuffer(data, np.uint8)
            return cv2.imdecode(np_data, cv2.IMREAD_UNCHANGED)

    @staticmethod
    def im2file(img: np.ndarray, fp: io.BufferedIOBase) -> bool:
        status, np_data = cv2.imencode('.png', img)
        np_data: np.ndarray
        fp.write(np_data.tobytes())
        return status

    @staticmethod
    def replace(
        img: np.ndarray,
        mask: np.ndarray,
        pos: Tuple[Tuple[int, int, int, int]]
    ):
        img = img.copy()
        # replace all !
        for (x, y, w, h) in pos:
            mask_res = cv2.resize(mask, (w, h))
            # Copy the resize image keeping the alpha channel
            for c in range(0, 3):
                img[y:y + h, x:x + w, c] = \
                    mask_res[:, :, c] * \
                    (mask_res[:, :, 3] / 255.0) + \
                    img[y:y + h, x:x + w, c] * \
                    (1.0 - (mask_res[:, :, 3] / 255.0))
        return img

    def detect(self, img: np.ndarray, adaptative: bool = True) -> Tuple[Tuple[int, int, int, int]]:
        # Convert to grays
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Equalize histogram, for improving contrast (this helps detection)
        if adaptative:
            gray = self.clahe.apply(gray)
        else:
            gray = cv2.equalizeHist(gray)

        return self.face_cc.detectMultiScale(gray, **self.face_cc_args)
