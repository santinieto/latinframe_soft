import unittest
from src.youtube import YoutubeVideo

class TestVideo(unittest.TestCase):

    def test_create_video_object(self):
        try:
            video_obj = YoutubeVideo()
        except Exception as e:
            self.fail(f"Could not create Video object.\n\tError value: {str(e)}")

    def test_create_empty_video(self):
        video = YoutubeVideo()
        self.assertEqual(None, video.id, 'Error while checking Video object generation')
        self.assertEqual('Unknown', video.title, 'Error while checking Video object generation')

    def test_get_video_id(self):
        video_id = 'tNba_Da5sHk'
        video = YoutubeVideo(id=video_id)
        self.assertEqual(video_id, video.id, 'Error while checking Video ID generation')

if __name__ == '__main__':
    unittest.main()