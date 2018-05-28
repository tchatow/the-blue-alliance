import re
import urlparse


class InternetArchiveVideoHelper(object):
    @classmethod
    def parse_id_from_url(cls, internet_archive_url):
        """
        Attempts to parse a URL for the video ID and timestamp (if present)
        Returns None if parsing fails
        """
        internet_archive_id = None
        internet_archive_video_file = None # Specifies a specific video in a playlist
        total_seconds = None

        # Try to parse for ID
        regex1 = re.match(r".*archive\.org\/details\/([a-zA-Z0-9_-]*)\/([a-zA-Z0-9_-]*)", internet_archive_url)
        if regex1 is not None:
            internet_archive_id = regex1.group(1)
            internet_archive_video_file = regex1.group(2)
        else:
            regex2 = re.match(r".*archive\.org\/embed\/([a-zA-Z0-9_-]*)\/([a-zA-Z0-9_-]*)", internet_archive_url)
            if regex2 is not None:
                internet_archive_id = regex2.group(1)
                internet_archive_video_file = regex2.group(2)
            else:
                regex3 = re.match(r".*archive\.org\/details\/([a-zA-Z0-9_-]*)", internet_archive_url)
                if regex3 is not None:
                    internet_archive_id = regex3.group(1)
                else:
                    regex4 = re.match(r".*archive\.org\/embed\/([a-zA-Z0-9_-]*)", internet_archive_url)
                    if regex4 is not None:
                        internet_archive_id = regex4.group(1)

        # Try to parse for time
        if internet_archive_id is not None:
            parsed = urlparse.urlparse(internet_archive_url)
            queries = urlparse.parse_qs(parsed.query)
            if 'start' in queries:
                total_seconds = queries['start'][0]
            elif parsed.fragment and 'start=' in parsed.fragment:
                total_seconds = parsed.fragment.split('start=')[1]

        if internet_archive_video_file is not None:
            internet_archive_id = '{}/{}'.format(internet_archive_id, internet_archive_video_file)
        if total_seconds is not None:
            internet_archive_id = '{}?start={}'.format(internet_archive_id, total_seconds)

        return internet_archive_id
