import cv2
import numpy


class ImageMatcher:
    def __init__(self, train_image):
        self.sift = cv2.SIFT_create()
        self.detector = self.sift
        self.descriptor = self.sift
        self.matcher = self._get_flann()
        self.homography = None
        self.homography_mask = None
        self.train_image = train_image
        self.train_keypoints = self.detector.detect(train_image, None)
        self.train_keypoints, self.train_descriptors = self.descriptor.compute(train_image, self.train_keypoints)

    def _get_flann(self):
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        return cv2.FlannBasedMatcher(index_params, search_params)

    def _get_brute_force(self):
        return cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)

    def get_homography(self, query_image):
        self.query_image = query_image
        self.query_keypoints = self.detector.detect(self.query_image, None)
        self.query_keypoints, self.query_descriptors = self.descriptor.compute(self.query_image, self.query_keypoints)

        nof_neighbours = 2
        matches = self.matcher.knnMatch(self.query_descriptors, self.train_descriptors, k=nof_neighbours)

        is_significantly_smaller_ratio = 0.7
        self.good_matches = []
        for match in matches:
            if len(match) < nof_neighbours:
                continue
            best_match, second_best_match = match
            if best_match.distance < is_significantly_smaller_ratio * second_best_match.distance:
                is_too_close = False
                for good_match in self.good_matches:
                    good_point = numpy.asarray(self.train_keypoints[good_match.trainIdx].pt)
                    best_point = numpy.asarray(self.train_keypoints[best_match.trainIdx].pt)
                    distance = cv2.norm(best_point - good_point)
                    if distance < 1:
                        is_too_close = True
                if not is_too_close:
                    self.good_matches.append(best_match)
        if len(self.good_matches) >= 4:
            self.src_pts = numpy.float32([self.query_keypoints[m.queryIdx].pt for m in self.good_matches]).reshape(
                -1, 1, 2
            )
            self.dst_pts = numpy.float32([self.train_keypoints[m.trainIdx].pt for m in self.good_matches]).reshape(
                -1, 1, 2
            )
            self.homography, self.homography_mask = cv2.findHomography(self.src_pts, self.dst_pts, cv2.RANSAC, 5.0)
            return self.homography

        return None


class VideoStabilizer:
    def __init__(self):
        self.sift = cv2.SIFT_create()
        self.detector = self.sift
        self.descriptor = self.sift
        self.matcher = self._get_flann()
        self.train_keypoints = None
        self.train_descriptors = None
        self.homography = None
        self.homography_mask = None

    def _get_flann(self):
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        return cv2.FlannBasedMatcher(index_params, search_params)

    def _get_brute_force(self):
        return cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)

    def get_homography(self, query_image):
        self._update(query_image)
        return self.homography

    def _update(self, query_image):
        query_keypoints = self.detector.detect(query_image, None)
        query_keypoints, query_descriptors = self.descriptor.compute(query_image, query_keypoints)
        if self.train_keypoints is None and self.train_descriptors is None:
            self.train_keypoints = query_keypoints
            self.train_descriptors = query_descriptors
        else:
            nof_neighbours = 2
            matches = self.matcher.knnMatch(query_descriptors, self.train_descriptors, k=nof_neighbours)

            is_significantly_smaller_ratio = 0.7
            good_matches = []
            for match in matches:
                if len(match) < nof_neighbours:
                    continue
                best_match, second_best_match = match
                if best_match.distance < is_significantly_smaller_ratio * second_best_match.distance:
                    good_matches.append(best_match)
            if len(good_matches) > 0:
                src_pts = numpy.float32([self.train_keypoints[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                dst_pts = numpy.float32([query_keypoints[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                self.homography, self.homography_mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

                self.train_keypoints = query_keypoints
                self.train_descriptors = query_descriptors
