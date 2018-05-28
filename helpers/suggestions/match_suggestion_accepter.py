from helpers.match_manipulator import MatchManipulator
from models.match import Match


class MatchSuggestionAccepter(object):
    """
    Handle accepting Match suggestions.
    """

    @classmethod
    def accept_suggestion(self, match, suggestion):
        if "youtube_videos" in suggestion.contents:
            match = self._merge_youtube_videos(match, suggestion.contents["youtube_videos"])
        elif "internet_archive_videos" in suggestion.contents:
            match = self._merge_internet_archive_videos(match, suggestion.contents["internet_archive_videos"])

        return MatchManipulator.createOrUpdate(match)

    @classmethod
    def _merge_youtube_videos(self, match, youtube_videos):
        for youtube_video in youtube_videos:
            if youtube_video not in match.youtube_videos:
                match.youtube_videos.append(youtube_video)

        return match

    @classmethod
    def _merge_internet_archive_videos(self, match, internet_archive_videos):
        for internet_archive_video in internet_archive_videos:
            if internet_archive_video not in match.internet_archive_videos:
                match.internet_archive_videos.append(internet_archive_video)

        return match
