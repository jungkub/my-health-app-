
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from data import questions, profiles
    from utils import calculate_scores, determine_profile, create_radar_chart

    print("Imports successful.")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)


def test_scoring():
    print("Testing scoring logic...")
    # Simulate answers: all choice 0
    answers = {q.id: 0 for q in questions}
    scores = calculate_scores(answers)
    print(f"Scores for all choice 0: {scores}")

    # Check if scores are integers
    assert all(isinstance(s, int) for s in scores.values())

    # Test profile determination
    profile = determine_profile(scores)
    print(f"Profile: {profile['desc']}")
    assert 'desc' in profile

    # Test chart creation
    try:
        fig = create_radar_chart(scores)
        print("Chart created successfully.")
    except Exception as e:
        print(f"Chart creation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_scoring()
    print("All tests passed!")
