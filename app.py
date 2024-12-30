import pandas as pd
import streamlit as st
from main import (
    fetch_channel_videos,
    fetch_video_metrics,
    train_model,
    suggest_topics,
    prepare_features,
)


# Function to automate the entire process
def automate_process(channel_id):
    # Fetch all videos from the channel
    st.write("Fetching videos from the channel...")
    videos = fetch_channel_videos(channel_id)
    st.write(f"Fetched {len(videos)} videos.")

    if not videos:
        st.error("No videos fetched.")
        return

    # Create DataFrame from video data
    video_data = pd.DataFrame(videos)
    st.write("Videos DataFrame created.")

    # Fetch video metrics (views, likes)
    st.write("Fetching video metrics...")
    metrics_data = []
    for video in videos:
        metrics = fetch_video_metrics(video["video_id"])
        metrics["video_id"] = video["video_id"]
        metrics_data.append(metrics)

    metrics_df = pd.DataFrame(metrics_data)

    # Merge video data with metrics
    merged_data = pd.merge(video_data, metrics_df, on="video_id", how="inner")
    st.write("Merged video data with metrics.")

    # Prepare the features for the model (including text processing and normalization)
    prepared_data = prepare_features(merged_data)
    st.write("Prepared features for the model.")

    # Train the model
    st.write("Training the model...")
    model = train_model(prepared_data)

    st.write("Model trained successfully!")

    return model, prepared_data


# Streamlit Interface
st.title("Content Brainstorming Assistant")

st.sidebar.header("Options")
option = st.sidebar.selectbox(
    "Choose an action", ("Automate Process", "Suggest Topics")
)

# Handle the "Automate Process" option
if option == "Automate Process":
    channel_id = st.text_input("Enter YouTube Channel ID", "UChVzP7gNOlkymoo000Y9_6Q")
    if st.button("Automate"):
        model, prepared_data = automate_process(channel_id)
        if model:
            # Optionally display some results here
            st.write("Displaying sample of prepared data:")
            st.write(
                prepared_data.head()
            )  # Show a small sample of the prepared data for the user

# Suggest Topics (using the trained model)
elif option == "Suggest Topics":
    if "model" not in locals():
        st.error("Please automate the process first to train the model.")
    else:
        new_topic_ideas = st.text_area("Enter new topic ideas (separate by commas)", "")
        if st.button("Suggest Topics"):
            if new_topic_ideas:
                suggestions = suggest_topics(new_topic_ideas.split(","), model)
                st.write("Suggested Topics and Predicted Popularity:")
                st.write(suggestions)
            else:
                st.error("Please enter some new topic ideas.")
