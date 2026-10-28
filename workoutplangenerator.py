import logging
import os

import groq
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
logger = logging.getLogger(__name__)


class PlanError(Exception):
    """A user-facing problem generating the plan."""

GOALS = ["Build muscle", "Lose fat", "General fitness", "Improve endurance"]
LEVELS = ["Beginner", "Intermediate", "Advanced"]
EQUIPMENT = ["No equipment", "Home dumbbells", "Full gym"]

SYSTEM_PROMPT = (
    "You are an experienced, certified personal trainer. You write safe, realistic, "
    "progressive weekly workout plans tailored to the client. You never invent "
    "equipment the client does not have, and you always respect stated injuries."
)

GUIDELINES = {
    "Beginner": "2-3 sets per exercise, simple compound or bodyweight movements, focus on form, RPE 6-7.",
    "Intermediate": "3-4 sets per exercise, mix of compound and isolation work, RPE 7-8, some progression scheme.",
    "Advanced": "4-5 sets for main lifts, periodization or intensity techniques, RPE 8-9, include deload advice.",
}


def build_prompt(
    goal: str,
    level: str,
    days_per_week: int,
    equipment: list[str],
    limitations: str,
) -> str:
    limits = limitations.strip() or "None reported"
    return f"""Create a {days_per_week}-day-per-week workout plan for this client.

CLIENT PROFILE
- Goal: {goal}
- Experience level: {level} ({GUIDELINES[level]})
- Training days per week: {days_per_week}
- Equipment available: {", ".join(equipment)}
- Injuries / limitations: {limits}

REQUIREMENTS
- Use ONLY the equipment listed. If "No equipment" is the only option, use bodyweight movements.
- Output exactly {days_per_week} training days, labelled "Day 1" to "Day {days_per_week}", then list the remaining days as rest/active recovery.
- Choose a split that suits {days_per_week} days and the goal (e.g. full body, upper/lower, push/pull/legs).
- For each day give: a focus title, a 5-minute warm-up, then a table of exercises with columns Exercise | Sets x Reps | Rest | Notes, and a short cool-down.
- Tailor volume, intensity and rest periods to the goal ({goal}) and level ({level}).
- Strictly avoid or substitute any movement that conflicts with the injuries/limitations above, and say which substitution you made.
- End with 3-4 bullets on progression (how to increase difficulty over the next 4 weeks) and one short safety note.
- Format in Markdown. Be specific and practical, no filler."""


def generate_workout_plan(
    goal: str,
    level: str,
    days_per_week: int,
    equipment: list[str],
    limitations: str = "",
) -> str:
    """Build the prompt, call Groq, and return the plan text. Raises PlanError with a friendly message."""
    if not 1 <= days_per_week <= 7:
        raise PlanError("Please choose between 1 and 7 training days per week.")
    if not equipment:
        raise PlanError("Please select at least one equipment option.")
    if goal not in GOALS or level not in LEVELS:
        raise PlanError("Please pick a valid goal and experience level.")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise PlanError("GROQ_API_KEY is missing. Add it to your .env file and restart the app.")

    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_prompt(goal, level, days_per_week, equipment, limitations),
                },
            ],
            temperature=0.6,
            max_tokens=3000,
        )
    except groq.AuthenticationError:
        raise PlanError("Your Groq API key was rejected. Please check GROQ_API_KEY.")
    except groq.RateLimitError:
        raise PlanError("Rate limit reached. Please wait a moment and try again.")
    except groq.APIConnectionError:
        raise PlanError("Couldn't reach Groq. Check your internet connection and try again.")
    except groq.APIStatusError as e:
        raise PlanError(f"Groq returned an error (status {e.status_code}). Please try again later.")
    except Exception:
        logger.exception("Unexpected error while generating workout plan")
        raise PlanError("Something went wrong while generating your plan. Please try again.")

    plan = (completion.choices[0].message.content or "").strip()
    if not plan:
        raise PlanError("The AI returned an empty plan. Please try again.")
    return plan


def main() -> None:
    st.set_page_config(page_title="Workout Plan Generator", page_icon="🏋️")
    st.title("🏋️ Personalized Workout Plan Generator")
    st.caption("Tell us about yourself and get a weekly plan built for you.")

    col1, col2 = st.columns(2)
    with col1:
        goal = st.selectbox("Fitness goal", GOALS)
        level = st.selectbox("Experience level", LEVELS)
    with col2:
        days = st.slider("Days available per week", 1, 7, 3)
        equipment = st.multiselect("Equipment access", EQUIPMENT, default=["Full gym"])
    limitations = st.text_area(
        "Injuries or limitations (optional)",
        placeholder='e.g. "bad knees", "no overhead pressing"',
    )

    if st.button("Generate Plan", type="primary"):
        try:
            with st.spinner("Your trainer is writing your plan..."):
                result = generate_workout_plan(goal, level, days, equipment, limitations)
        except PlanError as e:
            st.error(f"⚠️ {e}")
        else:
            st.divider()
            st.subheader("Your weekly plan")
            st.markdown(result)


if __name__ == "__main__":
    main()
