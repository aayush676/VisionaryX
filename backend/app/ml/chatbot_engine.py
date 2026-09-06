"""Future Self Chatbot.

A template + intent-classification engine that grounds every reply in the
user's real data: current Digital Twin state, AI Memory events, and active
goals. This is intentionally NOT a generative LLM by default -- it's an
honest, inspectable rule-based mentor so the app works standalone with zero
external API keys.

If LLM_PROVIDER / LLM_API_KEY are set in .env, `generate_reply` will attempt
`_try_llm_response` first (left as an integration point) and fall back to
the template engine on any failure or when unconfigured.
"""
import random

from app.core.config import get_settings

settings = get_settings()

_INTENT_KEYWORDS: dict[str, list[str]] = {
    "motivation": ["motivate", "motivation", "give up", "tired", "don't want to", "lazy", "unmotivated", "burnt out"],
    "goal_check": ["goal", "progress", "on track", "how am i doing", "am i doing well"],
    "habit_correction": ["sleep", "screen time", "procrastinat", "habit", "distracted", "phone"],
    "decision": ["should i", "decide", "decision", "choice", "what if", "which one"],
    "greeting": ["hi", "hello", "hey", "yo"],
}

_MODE_OPENERS: dict[str, list[str]] = {
    "mentor": ["Let's look at this clearly.", "Here's how I see it.", "Take a breath -- let's think this through."],
    "friend": ["Hey, I hear you.", "Okay real talk for a sec.", "I got you, let's figure this out."],
    "strict": ["No excuses -- let's be direct.", "Here's the truth, plainly.", "Cut the noise. Focus."],
    "growth": ["Every setback is data.", "This is exactly how growth happens.", "Let's reframe this."],
}

_TWIN_STATE_LINES: dict[str, dict[str, str]] = {
    "burnout": {
        "mentor": "Your Digital Twin is showing Burnout signals right now -- your future self needs you to rest before pushing further.",
        "friend": "Your twin's flashing burnout mode. Seriously, go rest a bit before grinding more.",
        "strict": "Burnout state detected. Continuing to push through this is how you lose weeks, not gain them.",
        "growth": "Burnout is a signal, not a failure -- it's telling you the current pace isn't sustainable. Adjust, don't quit.",
    },
    "distracted": {
        "mentor": "I'm noticing a Distracted pattern in your recent habits -- your focus and consistency have both dipped.",
        "friend": "Looks like you've been a bit scattered lately, focus-wise.",
        "strict": "You're in a Distracted state. That's lost time you won't get back.",
        "growth": "Distraction is fixable with one small consistent habit -- let's find it.",
    },
    "nominal": {
        "mentor": "You're in a steady, Nominal state -- solid, but there's room to push toward Focused.",
        "friend": "You're doing fine, nothing dramatic either way.",
        "strict": "Nominal isn't good enough if you want elite outcomes. Raise the bar.",
        "growth": "Nominal is a stable base -- a great place to layer in one new habit.",
    },
    "focused": {
        "mentor": "You're in a Focused state right now -- your consistency is paying off.",
        "friend": "You're locked in lately, keep that energy!",
        "strict": "Good. Focused. Don't get comfortable -- push for Elite.",
        "growth": "Focused is proof your systems are working -- notice what's different and keep it.",
    },
    "elite_performer": {
        "mentor": "You're operating as an Elite Performer right now -- this is what consistency compounding looks like.",
        "friend": "Okay you're literally crushing it right now.",
        "strict": "Elite state. Maintain it -- this is the standard now, not the ceiling.",
        "growth": "This Elite state is the result of every small choice you've made -- study what's working.",
    },
}


def detect_intent(message: str) -> str:
    text = message.lower()
    for intent, keywords in _INTENT_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return intent
    return "general"


def _memory_line(memory_context: list[str], mode: str) -> str | None:
    if not memory_context:
        return None
    memory = memory_context[0]
    prefixes = {
        "mentor": "Something worth remembering:",
        "friend": "Also, don't forget --",
        "strict": "One fact you can't ignore:",
        "growth": "Here's context that matters:",
    }
    return f"{prefixes.get(mode, 'Note:')} {memory}"


def _goal_line(active_goal_titles: list[str], mode: str) -> str | None:
    if not active_goal_titles:
        return None
    titles = ", ".join(active_goal_titles[:3])
    lines = {
        "mentor": f"Your active goals right now are: {titles}. Which one needs attention today?",
        "friend": f"You've still got {titles} going -- how's that feeling?",
        "strict": f"Your open goals: {titles}. Pick one and move it forward today.",
        "growth": f"{titles} are all opportunities to compound -- small daily input, big output later.",
    }
    return lines.get(mode)


def _intent_body(intent: str, mode: str) -> str:
    bodies: dict[str, dict[str, str]] = {
        "motivation": {
            "mentor": "Motivation fades, but systems don't -- what's one small action you can take in the next 10 minutes?",
            "friend": "It's okay to feel low on drive sometimes. Just start with something tiny today.",
            "strict": "Motivation is irrelevant. Discipline is what moves you forward -- act now, feel later.",
            "growth": "Low motivation is a normal phase in any growth curve, not a stop sign.",
        },
        "goal_check": {
            "mentor": "Based on your data, your consistency is the biggest lever for your goals right now.",
            "friend": "You're making progress, even if it doesn't always feel like it day to day.",
            "strict": "Check your progress numbers honestly. If they're flat, something has to change today.",
            "growth": "Progress isn't linear -- what matters is the trend over the last few weeks.",
        },
        "habit_correction": {
            "mentor": "Small shifts in sleep and screen time tend to move your whole trajectory more than people expect.",
            "friend": "Maybe try cutting screen time by even 30 minutes tonight and see how tomorrow feels.",
            "strict": "Fix the habit today. Not tomorrow. Today.",
            "growth": "Every habit you correct now compounds into your future self's baseline.",
        },
        "decision": {
            "mentor": "Try running this through the What-If Simulator -- see how each option shifts your future outcomes before committing.",
            "friend": "Honestly, run the numbers in the simulator, that usually makes the choice obvious.",
            "strict": "Stop deliberating. Simulate both paths, pick the higher-readiness one, and commit.",
            "growth": "Neither choice is wrong -- what matters is what you learn from whichever you pick.",
        },
        "greeting": {
            "mentor": "Good to see you. What's on your mind today?",
            "friend": "Hey! What's up?",
            "strict": "You're here. Good. What are we fixing today?",
            "growth": "Welcome back -- ready to build on yesterday?",
        },
        "general": {
            "mentor": "Tell me more about what's going on, and I'll help you think it through.",
            "friend": "I'm listening -- what's going on?",
            "strict": "Be specific. What outcome are you trying to change?",
            "growth": "Every conversation here is a chance to recalibrate -- what's the real question underneath this?",
        },
    }
    return bodies.get(intent, bodies["general"]).get(mode, bodies["general"]["mentor"])


def _try_llm_response(message: str, mode: str, context: dict) -> str | None:
    """Integration point for a real LLM. Returns None (falls back to
    templates) unless LLM_PROVIDER/LLM_API_KEY are configured and wired up."""
    if not settings.llm_provider or not settings.llm_api_key:
        return None
    # Intentionally left unimplemented: wire your provider's SDK here and
    # pass `context` (twin state, memory, goals) in as grounding.
    return None


def generate_reply(
    message: str,
    mode: str,
    twin_state: str,
    memory_context: list[str],
    active_goal_titles: list[str],
) -> str:
    llm_reply = _try_llm_response(message, mode, {
        "twin_state": twin_state, "memory": memory_context, "goals": active_goal_titles,
    })
    if llm_reply:
        return llm_reply

    mode = mode if mode in _MODE_OPENERS else "mentor"
    intent = detect_intent(message)

    parts = [random.choice(_MODE_OPENERS[mode])]
    parts.append(_intent_body(intent, mode))

    if intent != "greeting":
        twin_line = _TWIN_STATE_LINES.get(twin_state, {}).get(mode)
        if twin_line:
            parts.append(twin_line)

        memory_line = _memory_line(memory_context, mode)
        if memory_line:
            parts.append(memory_line)

        if intent == "goal_check":
            goal_line = _goal_line(active_goal_titles, mode)
            if goal_line:
                parts.append(goal_line)

    return " ".join(parts)
