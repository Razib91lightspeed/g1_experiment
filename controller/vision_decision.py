import json
import subprocess

from spark_client.vlm_client import analyze_image

IMAGE = "camera/g1_frame.jpg"


def main():
    print("=== G1 Vision-Based Decision ===")

    # Capture a fresh image from the robot.
    subprocess.run(
        ["./scripts/capture_g1_frame.sh"],
        check=True
    )

    # Ask Spark whether a person is visible.
    response = analyze_image(IMAGE)

    try:
        result = json.loads(response)
    except json.JSONDecodeError:
        print("Invalid VLM response. No action.")
        return

    # Accept an explicit boolean, never a guessed value.
    person_visible = result.get("person_visible")

    if type(person_visible) is not bool:
        print("Invalid detection result. No action.")
        return

    if person_visible:
        action = "wave"
    else:
        action = "no_action"

    print("\n=== AI DECISION ===")
    print("Person visible:", person_visible)
    print("Proposed action:", action)
    print("Execution: DRY RUN")
    print("Robot movement: DISABLED")


if __name__ == "__main__":
    main()
