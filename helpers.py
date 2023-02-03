import whisper
import youtube_dl
import tempfile
import pathlib
import json


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d["status"] == "downloading":
        print(
            f"File downloading at {d['speed']}, estimated time rem: {d['eta']} seconds"
            "\n{}"
        )
    if d["status"] == "finished":
        print("Done downloading, now converting ...")


def make_safe_filename(s):
    def safe_char(c):
        if c.isalnum():
            return c
        else:
            return "_"

    return "".join(safe_char(c) for c in s).rstrip("_")


def download_from_url(url, output_loc):
    output_name = make_safe_filename(url)
    output_templ = f"{output_loc}/{output_name}"
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "logger": MyLogger(),
        "progress_hooks": [my_hook],
        "writeinfojson": False,
        "outtmpl": f"{output_templ}_%(title)s.%(ext)s",
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=True)

    files = sorted(pathlib.Path(output_loc).glob("*.mp3"))
    for f in files:
        f.rename(f.parent / f"{make_safe_filename(f.name)}{f.suffix}")


def load_whisper_model(model: str = "base.en", device: str = None):
    if not device:
        device = "cpu"
    model = whisper.load_model(model, device=device)
    return model


def transcribe_audio_file(file_path):
    # empty list to store file names once done, probably dont need?
    # transcript_paths = []

    model = load_whisper_model()
    result = model.transcribe(file_path, fp16=False, language="English")
    whisper.utils.get_writer(output_format="txt", output_dir="outputs/")(
        result, file_path
    )

    return result["text"]
    # TODO: return list of filenames outputted? maybe check against pre-computed list \
    # of filenames from url. May not be necessary, streamlit may be able to just cache \
    # function and know not to recompute?


def transcribe_audio_from_url(url):
    # set temp dir location to cwd
    tempfile.tempdir = pathlib.Path().resolve()

    # empty structure to house model results
    model_results = []

    # initialize temp dir w/ context manager, will be deleted once out of scope
    # download file(s) and transcribe with whisper
    # save outputs, downloads are deleted
    with tempfile.TemporaryDirectory() as tmpdirname:
        output_loc = tmpdirname.decode()
        download_from_url(url, output_loc)
        files = sorted(pathlib.Path(output_loc).glob("*.mp3"))
        for f in files:
            fname = str(f.name)
            model_transcript = transcribe_audio_file(str(f))
            transcript_json = json.dumps({fname: model_transcript})
            model_results.append(transcript_json)
    return model_results


def summarize_transcript(transcript):
    pass


if __name__ == "__main__":
    import pprint

    # url = "https://www.youtube.com/watch?v=WlY9pDwGbjw"
    url = "https://www.youtube.com/watch?v=gjVwjISLPZo"
    # url = "https://www.police1.com/active-shooter/videos/santa-barbara-killers-retribution-video-cvhbBxq4q7mDgTiK/"
    # url = "https://archive.org/details/elliotrodgermanifestomytwistedworld"
    pprint.pprint(transcribe_audio_from_url(url))
