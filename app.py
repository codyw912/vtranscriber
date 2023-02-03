import streamlit as st
import helpers


def main():
    # Streamlit config
    st.set_page_config(
        page_title="Video Transcription with Whisper",
        layout="centered",
    )
    # Title
    st.markdown("# Video Transcription with Whisper")

    # Intro text
    st.markdown(
        """
        This Streamlit app lets you transcribe videos from various sources using 
        [Whisper](https://github.com/openai/whisper). 
        Uses [youtube-dl](https://github.com/ytdl-org/youtube-dl) to download and
        extract audio from the video sources. 
        """
    )

    available_whisper_models = ["tiny.en", "base.en"]

    # Let user choose whisper model
    @st.cache(show_spinner=True)
    def load_whisper_model(model: str = "base.en"):
        return helpers.load_whisper_model(model=model)

    # Title: Input data
    st.markdown("## Select model and input url")

    st.markdown(
        "Models listed from fastest to slowest: tiny, base -- \
    slower models can be more accurate, but will take substantially longer to run. \
    Only supports tiny and base models as compute is limited."
    )

    # model selection option
    model_input_option = st.selectbox(
        "Model:", options=["Choose a model:"] + available_whisper_models
    )

    if model_input_option == "Choose a model:":
        selected_whisper_model = None

    else:
        selected_whisper_model = model_input_option

    if selected_whisper_model:
        # Load Whisper model
        with st.spinner("Loading selected Whisper model..."):
            model = load_whisper_model(selected_whisper_model)

        url = st.text_input("Enter a video url:")

        if url:
            chat_gpt_summarize = st.checkbox("Summarize using ChatGPT")

            st.markdown("## Output")

            @st.cache(show_spinner=True)
            def transcribe_audio_wrapped(url):
                return helpers.transcribe_audio_from_url(url)

            if st.button("Generate Transcript"):
                with st.spinner("Transcribing audio... this may take a few minutes."):
                    transcripts_json = transcribe_audio_wrapped(url)

                st.json(transcripts_json)

        else:
            st.warning("Please enter a video URL.")

    else:
        st.warning("Please select a whisper model from the dropdown.")


if __name__ == "__main__":
    main()
