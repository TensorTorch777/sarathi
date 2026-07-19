#!/usr/bin/env python3
"""
One-time content authoring helper: emit Chapter 2 Sarathi Intelligence drafts.

Not a runtime service. Output is reviewed by humans before approval.
Does not modify Layer 1 (bhagavad_gita.json).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = (
    ROOT
    / "data"
    / "corpus"
    / "bhagavad_gita"
    / "sarathi_intelligence"
    / "chapter_02.draft.json"
)

# Hand-authored draft enrichments. status is always draft.
# confidence: 0–1 editorial certainty (not model probability theater).
DRAFTS: dict[int, dict] = {
    1: {
        "summary": "Sanjaya describes Arjuna overwhelmed by compassion and tears before Krishna speaks.",
        "modern_interpretation": "When grief floods the body, wise counsel often begins with simply naming the collapse — not rushing to fix it.",
        "topics": ["compassion", "mind"],
        "emotions": ["grief", "overwhelm"],
        "life_domains": ["family", "relationships", "identity"],
        "user_intents": ["seeking_guidance", "seeking_peace"],
        "virtues": ["compassion", "patience"],
        "practice": ["Name what you feel in one honest sentence before deciding anything."],
        "reflection_question": "Where am I so flooded that I cannot yet hear guidance?",
        "related_verses": ["bg_2_2", "bg_2_7", "bg_2_11"],
        "confidence": {"summary": 0.9, "topics": 0.75, "emotions": 0.85, "overall": 0.85},
        "uncertainty_notes": "Emotion tags lean pastoral; battlefield context is also political/dharma conflict.",
    },
    2: {
        "summary": "Krishna challenges Arjuna: this despair in crisis is unworthy and self-diminishing.",
        "modern_interpretation": "Compassion is noble; paralysis dressed as virtue can still shrink you when action is required.",
        "topics": ["duty", "courage", "dharma"],
        "emotions": ["confusion", "fear", "shame"],
        "life_domains": ["career", "leadership", "identity"],
        "user_intents": ["seeking_courage", "seeking_guidance"],
        "virtues": ["courage", "honesty"],
        "practice": ["Ask: is this pause wisdom, or am I avoiding a hard duty?"],
        "reflection_question": "What weakness am I currently calling 'kindness'?",
        "related_verses": ["bg_2_3", "bg_2_31", "bg_2_37"],
        "confidence": {"summary": 0.85, "topics": 0.8, "emotions": 0.7, "overall": 0.8},
        "uncertainty_notes": "Tone is sharp; Sarathi should deliver with care, never shaming.",
    },
    3: {
        "summary": "Reject small-heartedness; stand up — this frailty does not fit you.",
        "modern_interpretation": "Sometimes the most compassionate word is: you are stronger than this collapse.",
        "topics": ["courage", "duty", "self"],
        "emotions": ["fear", "hopelessness", "shame"],
        "life_domains": ["career", "leadership", "identity"],
        "user_intents": ["seeking_courage", "seeking_encouragement"],
        "virtues": ["courage", "discipline"],
        "practice": ["Stand up — literally — and take one concrete next step."],
        "reflection_question": "What would 'standing up' look like in my situation today?",
        "related_verses": ["bg_2_2", "bg_2_37", "bg_2_38"],
        "confidence": {"summary": 0.9, "topics": 0.85, "emotions": 0.8, "overall": 0.85},
        "uncertainty_notes": None,
    },
    4: {
        "summary": "Arjuna asks how he can fight revered teachers Bhishma and Drona.",
        "modern_interpretation": "Conflict hurts most when duty seems to demand opposing people we love and respect.",
        "topics": ["dharma", "family", "duty"],
        "emotions": ["grief", "guilt", "confusion"],
        "life_domains": ["family", "relationships", "leadership"],
        "user_intents": ["seeking_guidance", "seeking_forgiveness"],
        "virtues": ["humility", "honesty"],
        "practice": ["Write the names of people you fear disappointing; separate love from agreement."],
        "reflection_question": "Where does loyalty to people collide with loyalty to truth?",
        "related_verses": ["bg_2_5", "bg_2_6", "bg_2_7"],
        "confidence": {"summary": 0.9, "topics": 0.8, "emotions": 0.85, "overall": 0.85},
        "uncertainty_notes": "family is not in topics taxonomy — mapped via life_domains.",
    },
    5: {
        "summary": "Arjuna would rather live by begging than enjoy gains won by killing elders.",
        "modern_interpretation": "When success would require betraying your conscience, even 'winning' can feel like spiritual poverty.",
        "topics": ["dharma", "renunciation", "duty"],
        "emotions": ["guilt", "grief", "confusion"],
        "life_domains": ["career", "money", "family"],
        "user_intents": ["seeking_meaning", "seeking_guidance"],
        "virtues": ["honesty", "humility"],
        "practice": ["Name one success you would refuse if it cost your integrity."],
        "reflection_question": "What am I unwilling to gain if the price is becoming someone I cannot respect?",
        "related_verses": ["bg_2_4", "bg_2_6", "bg_2_33"],
        "confidence": {"summary": 0.85, "topics": 0.75, "emotions": 0.8, "overall": 0.8},
        "uncertainty_notes": "Modern mapping to career ethics is interpretive.",
    },
    6: {
        "summary": "Arjuna cannot tell which is better — victory or defeat — when either costs unbearable loss.",
        "modern_interpretation": "Some decisions feel lose-lose; clarity begins by admitting you truly do not know yet.",
        "topics": ["dharma", "wisdom", "mind"],
        "emotions": ["confusion", "overwhelm", "fear"],
        "life_domains": ["family", "career", "identity"],
        "user_intents": ["seeking_guidance", "seeking_peace"],
        "virtues": ["humility", "patience"],
        "practice": ["Say out loud: 'I do not know yet' — then seek counsel, not noise."],
        "reflection_question": "Where am I forcing a binary when I am still confused?",
        "related_verses": ["bg_2_7", "bg_2_8", "bg_2_11"],
        "confidence": {"summary": 0.9, "topics": 0.8, "emotions": 0.85, "overall": 0.85},
        "uncertainty_notes": None,
    },
    7: {
        "summary": "Broken by softness of heart and confused about dharma, Arjuna asks as a student for what is truly good.",
        "modern_interpretation": "The turning point of wisdom is not clever argument — it is surrendering confusion and asking for what is truly wholesome.",
        "topics": ["dharma", "wisdom", "surrender"],
        "emotions": ["confusion", "grief", "hopelessness"],
        "life_domains": ["spiritual_practice", "identity", "family"],
        "user_intents": ["seeking_guidance", "seeking_meaning"],
        "virtues": ["humility", "honesty", "devotion"],
        "practice": ["Ask one trusted guide a single clear question: what is truly good for me to do?"],
        "reflection_question": "Am I arguing to win, or am I ready to be taught?",
        "related_verses": ["bg_2_8", "bg_2_11", "bg_2_39"],
        "confidence": {"summary": 0.95, "topics": 0.9, "emotions": 0.85, "overall": 0.9},
        "uncertainty_notes": None,
    },
    8: {
        "summary": "No worldly success can remove the grief drying up Arjuna's senses.",
        "modern_interpretation": "Achievement cannot anesthetize grief; some pain needs meaning, not more trophies.",
        "topics": ["mind", "wisdom", "detachment"],
        "emotions": ["grief", "hopelessness", "overwhelm"],
        "life_domains": ["career", "money", "identity"],
        "user_intents": ["seeking_peace", "seeking_meaning"],
        "virtues": ["honesty", "patience"],
        "practice": ["List what you hoped success would heal — then admit what it cannot."],
        "reflection_question": "What am I trying to buy or win to silence a sorrow that needs facing?",
        "related_verses": ["bg_2_7", "bg_2_11", "bg_2_14"],
        "confidence": {"summary": 0.9, "topics": 0.8, "emotions": 0.9, "overall": 0.85},
        "uncertainty_notes": None,
    },
    9: {
        "summary": "Arjuna refuses to fight and falls silent before Krishna.",
        "modern_interpretation": "Sometimes collapse ends in silence — not as peace, but as the moment before a deeper teaching can begin.",
        "topics": ["mind", "duty", "surrender"],
        "emotions": ["hopelessness", "overwhelm", "fear"],
        "life_domains": ["identity", "leadership", "spiritual_practice"],
        "user_intents": ["seeking_guidance", "seeking_peace"],
        "virtues": ["honesty", "humility"],
        "practice": ["If you are stuck, stop performing answers; sit quietly for two minutes first."],
        "reflection_question": "Is my silence receptivity — or shutdown?",
        "related_verses": ["bg_2_7", "bg_2_10", "bg_2_11"],
        "confidence": {"summary": 0.9, "topics": 0.7, "emotions": 0.8, "overall": 0.8},
        "uncertainty_notes": "Silence can mean many things; tagged as overwhelm with medium confidence.",
    },
    10: {
        "summary": "Between the two armies, Krishna begins to address the grieving Arjuna.",
        "modern_interpretation": "Guidance often arrives in the middle of the conflict — not after life becomes tidy.",
        "topics": ["wisdom", "dharma", "compassion"],
        "emotions": ["grief", "anxiety"],
        "life_domains": ["spiritual_practice", "leadership"],
        "user_intents": ["seeking_guidance"],
        "virtues": ["compassion", "patience"],
        "practice": ["Seek wisdom while still in the difficulty, not only after it ends."],
        "reflection_question": "Am I waiting for perfect calm before I am willing to learn?",
        "related_verses": ["bg_2_1", "bg_2_11", "bg_2_39"],
        "confidence": {"summary": 0.85, "topics": 0.7, "emotions": 0.7, "overall": 0.75},
        "uncertainty_notes": "Transitional narrative verse; enrichment is lighter by design.",
    },
    11: {
        "summary": "The wise do not grieve for the living or the dead as the confused do.",
        "modern_interpretation": "Grief is human; wisdom does not forbid feeling — it refuses despair that treats change as final annihilation.",
        "topics": ["wisdom", "equanimity", "liberation"],
        "emotions": ["grief", "confusion"],
        "life_domains": ["grief_loss", "family", "spiritual_practice"],
        "user_intents": ["seeking_peace", "seeking_meaning"],
        "virtues": ["wisdom", "equanimity", "patience"],
        "practice": ["When grief rises, add one true sentence: 'This changes form; love is not erased.'"],
        "reflection_question": "What am I grieving as if it were absolute disappearance?",
        "related_verses": ["bg_2_13", "bg_2_20", "bg_2_27"],
        "confidence": {"summary": 0.9, "topics": 0.85, "emotions": 0.8, "overall": 0.85},
        "uncertainty_notes": "Must not be used to invalidate healthy mourning.",
    },
    12: {
        "summary": "There was never a time when we did not exist; nor shall we cease to be.",
        "modern_interpretation": "Your deepest identity is not a temporary role — existence itself is more continuous than fear claims.",
        "topics": ["self", "wisdom", "liberation"],
        "emotions": ["fear", "grief", "anxiety"],
        "life_domains": ["identity", "grief_loss", "spiritual_practice"],
        "user_intents": ["seeking_meaning", "seeking_peace"],
        "virtues": ["wisdom", "courage"],
        "practice": ["Quietly affirm: I am more than this temporary role or crisis."],
        "reflection_question": "What temporary identity am I mistaking for my whole self?",
        "related_verses": ["bg_2_13", "bg_2_20", "bg_2_22"],
        "confidence": {"summary": 0.9, "topics": 0.9, "emotions": 0.75, "overall": 0.85},
        "uncertainty_notes": None,
    },
    13: {
        "summary": "As the embodied self passes childhood, youth, and age, so it passes to another body — the wise are not bewildered.",
        "modern_interpretation": "Life is a sequence of forms; clinging to one stage as permanent creates unnecessary panic.",
        "topics": ["self", "wisdom", "equanimity"],
        "emotions": ["fear", "grief", "anxiety"],
        "life_domains": ["health", "identity", "grief_loss"],
        "user_intents": ["seeking_peace", "seeking_courage"],
        "virtues": ["wisdom", "equanimity", "patience"],
        "practice": ["Notice one life stage you are resisting; name what is ending and what continues."],
        "reflection_question": "Which change am I treating as annihilation rather than transition?",
        "related_verses": ["bg_2_12", "bg_2_22", "bg_2_27"],
        "confidence": {"summary": 0.95, "topics": 0.9, "emotions": 0.8, "overall": 0.9},
        "uncertainty_notes": None,
    },
    14: {
        "summary": "Sensations of heat and cold, pleasure and pain come and go — endure them.",
        "modern_interpretation": "Moods and sensory storms are temporary weather; you can feel them without crowning them as identity.",
        "topics": ["equanimity", "mind", "discipline"],
        "emotions": ["anxiety", "grief", "anger"],
        "life_domains": ["health", "career", "relationships"],
        "user_intents": ["seeking_peace", "seeking_discipline"],
        "virtues": ["patience", "equanimity", "self_control"],
        "practice": ["When discomfort spikes, label it: 'temporary contact' — breathe for one minute."],
        "reflection_question": "Which passing sensation am I currently obeying as if it were permanent truth?",
        "related_verses": ["bg_2_15", "bg_2_38", "bg_2_56"],
        "confidence": {"summary": 0.95, "topics": 0.9, "emotions": 0.85, "overall": 0.9},
        "uncertainty_notes": None,
    },
    15: {
        "summary": "The person whom these dualities do not torment becomes fit for immortality.",
        "modern_interpretation": "Emotional steadiness is not numbness; it is resilience that can hold joy and pain without collapse.",
        "topics": ["equanimity", "liberation", "wisdom"],
        "emotions": ["anxiety", "peace"],
        "life_domains": ["spiritual_practice", "health", "leadership"],
        "user_intents": ["seeking_peace", "seeking_courage"],
        "virtues": ["equanimity", "courage", "patience"],
        "practice": ["In the next difficult hour, aim for steadiness rather than positivity."],
        "reflection_question": "Can I let pleasure and pain move through me without becoming either?",
        "related_verses": ["bg_2_14", "bg_2_38", "bg_2_56"],
        "confidence": {"summary": 0.9, "topics": 0.85, "emotions": 0.7, "overall": 0.85},
        "uncertainty_notes": None,
    },
    16: {
        "summary": "The unreal has no lasting being; the real never ceases — seers know this boundary.",
        "modern_interpretation": "Separate what is fleeting from what is enduring; much anxiety comes from treating the temporary as absolute.",
        "topics": ["wisdom", "knowledge", "liberation"],
        "emotions": ["confusion", "anxiety", "fear"],
        "life_domains": ["identity", "spiritual_practice", "career"],
        "user_intents": ["seeking_meaning", "seeking_peace"],
        "virtues": ["wisdom", "honesty"],
        "practice": ["Sort today's worries into 'passing' vs 'enduring' — act only on what is truly yours."],
        "reflection_question": "What unreal thing am I treating as ultimate?",
        "related_verses": ["bg_2_17", "bg_2_20", "bg_2_45"],
        "confidence": {"summary": 0.85, "topics": 0.85, "emotions": 0.65, "overall": 0.8},
        "uncertainty_notes": "Metaphysical verse; modern mapping is necessarily interpretive.",
    },
    17: {
        "summary": "Know that by which all this is pervaded as indestructible — none can destroy it.",
        "modern_interpretation": "There is a ground of being that fear cannot erase; remembering it softens panic about loss.",
        "topics": ["self", "wisdom", "liberation"],
        "emotions": ["fear", "anxiety"],
        "life_domains": ["spiritual_practice", "grief_loss", "identity"],
        "user_intents": ["seeking_peace", "seeking_courage"],
        "virtues": ["wisdom", "courage"],
        "practice": ["In fear, place a hand on your chest and remember: something essential remains."],
        "reflection_question": "What in me cannot be taken by this loss?",
        "related_verses": ["bg_2_16", "bg_2_20", "bg_2_24"],
        "confidence": {"summary": 0.85, "topics": 0.85, "emotions": 0.75, "overall": 0.8},
        "uncertainty_notes": None,
    },
    18: {
        "summary": "Bodies are perishable; the embodied self is said to be eternal — therefore fulfill your duty.",
        "modern_interpretation": "Mortality of form does not cancel responsibility; it clarifies what courage is for.",
        "topics": ["duty", "self", "dharma"],
        "emotions": ["fear", "grief"],
        "life_domains": ["leadership", "spiritual_practice", "identity"],
        "user_intents": ["seeking_courage", "seeking_guidance"],
        "virtues": ["courage", "discipline", "wisdom"],
        "practice": ["Do the next right action even while acknowledging impermanence."],
        "reflection_question": "Am I using mortality as an excuse to freeze — or as a reason to act cleanly?",
        "related_verses": ["bg_2_17", "bg_2_30", "bg_2_31"],
        "confidence": {"summary": 0.85, "topics": 0.8, "emotions": 0.75, "overall": 0.8},
        "uncertainty_notes": "Battlefield 'fight' maps carefully to modern 'fulfill duty' — avoid martial glorification.",
    },
    19: {
        "summary": "One who thinks the Self kills or is killed understands neither — it neither kills nor is killed.",
        "modern_interpretation": "The deepest self is not reduced to the drama of harm and victory that the ego obsesses over.",
        "topics": ["self", "wisdom", "liberation"],
        "emotions": ["fear", "guilt", "confusion"],
        "life_domains": ["spiritual_practice", "identity"],
        "user_intents": ["seeking_meaning", "seeking_peace"],
        "virtues": ["wisdom", "non_attachment"],
        "practice": ["When guilt spirals, ask: am I confusing role-action with my deepest being?"],
        "reflection_question": "Where am I over-identifying with a temporary role of 'doer' or 'victim'?",
        "related_verses": ["bg_2_20", "bg_2_21", "bg_2_30"],
        "confidence": {"summary": 0.85, "topics": 0.85, "emotions": 0.7, "overall": 0.8},
        "uncertainty_notes": "Do not misuse to dismiss real ethical responsibility.",
    },
    20: {
        "summary": "The Self is unborn, eternal, ancient; it is not slain when the body is slain.",
        "modern_interpretation": "Fear of total erasure softens when you remember that consciousness is not identical with a fragile body-story.",
        "topics": ["self", "liberation", "wisdom"],
        "emotions": ["fear", "grief", "peace"],
        "life_domains": ["grief_loss", "spiritual_practice", "health"],
        "user_intents": ["seeking_peace", "seeking_courage"],
        "virtues": ["wisdom", "courage", "equanimity"],
        "practice": ["In mortality anxiety, recite quietly: unborn, eternal — then return to kindness here."],
        "reflection_question": "What would change if I trusted that my being is deeper than this body-fear?",
        "related_verses": ["bg_2_12", "bg_2_17", "bg_2_22"],
        "confidence": {"summary": 0.95, "topics": 0.9, "emotions": 0.8, "overall": 0.9},
        "uncertainty_notes": None,
    },
    21: {
        "summary": "Knowing the Self as indestructible, how can one cause killing or be killed in truth?",
        "modern_interpretation": "Insight into the Self reorients violence and fear — not by apathy, but by seeing beyond ego-drama.",
        "topics": ["self", "wisdom", "detachment"],
        "emotions": ["fear", "guilt", "confusion"],
        "life_domains": ["spiritual_practice", "identity"],
        "user_intents": ["seeking_meaning", "seeking_detachment"],
        "virtues": ["wisdom", "non_attachment"],
        "practice": ["Before a harsh judgment, pause: what is temporary role, what is deeper being?"],
        "reflection_question": "Where does ego-drama exaggerate my power to destroy or be destroyed?",
        "related_verses": ["bg_2_19", "bg_2_20", "bg_2_30"],
        "confidence": {"summary": 0.8, "topics": 0.8, "emotions": 0.65, "overall": 0.75},
        "uncertainty_notes": "Ethically sensitive; keep away from justifying harm.",
    },
    22: {
        "summary": "As one discards worn clothes for new, the embodied self discards worn bodies.",
        "modern_interpretation": "Change of form can be dignified rather than catastrophic — endings make space for continuation.",
        "topics": ["self", "wisdom", "equanimity"],
        "emotions": ["grief", "fear", "peace"],
        "life_domains": ["grief_loss", "health", "identity"],
        "user_intents": ["seeking_peace", "seeking_courage"],
        "virtues": ["wisdom", "equanimity", "patience"],
        "practice": ["Ritualize a small ending today: thank what is worn out before releasing it."],
        "reflection_question": "What 'worn garment' in my life am I refusing to set down?",
        "related_verses": ["bg_2_13", "bg_2_20", "bg_2_27"],
        "confidence": {"summary": 0.95, "topics": 0.9, "emotions": 0.85, "overall": 0.9},
        "uncertainty_notes": None,
    },
    23: {
        "summary": "Weapons cannot cut the Self, fire cannot burn it, water cannot wet it, wind cannot dry it.",
        "modern_interpretation": "Your deepest awareness is not as fragile as circumstance insists — this can stabilize panic without denying pain.",
        "topics": ["self", "liberation", "wisdom"],
        "emotions": ["fear", "anxiety", "peace"],
        "life_domains": ["spiritual_practice", "health", "identity"],
        "user_intents": ["seeking_courage", "seeking_peace"],
        "virtues": ["courage", "wisdom"],
        "practice": ["In panic, name four threats — then remember what they cannot touch in you."],
        "reflection_question": "What am I protecting as if my whole being could be destroyed by it?",
        "related_verses": ["bg_2_20", "bg_2_24", "bg_2_25"],
        "confidence": {"summary": 0.9, "topics": 0.9, "emotions": 0.8, "overall": 0.85},
        "uncertainty_notes": None,
    },
    24: {
        "summary": "The Self is uncleavable, unburnable, eternal, all-pervading, immovable, everlasting.",
        "modern_interpretation": "Stability is not stubbornness of ego; it is resting in what does not depend on today's outcome.",
        "topics": ["self", "liberation", "equanimity"],
        "emotions": ["anxiety", "fear", "peace"],
        "life_domains": ["spiritual_practice", "identity"],
        "user_intents": ["seeking_peace", "seeking_meaning"],
        "virtues": ["equanimity", "wisdom"],
        "practice": ["Sit unmoving for three minutes; watch thoughts pass without chasing them."],
        "reflection_question": "Where am I seeking permanence in the wrong place?",
        "related_verses": ["bg_2_23", "bg_2_25", "bg_2_17"],
        "confidence": {"summary": 0.9, "topics": 0.85, "emotions": 0.75, "overall": 0.85},
        "uncertainty_notes": None,
    },
    25: {
        "summary": "The Self is unmanifest, inconceivable, unchanging — therefore do not grieve.",
        "modern_interpretation": "Not everything real is graspable by anxious thinking; peace can come from releasing the need to fully conceptualize.",
        "topics": ["self", "wisdom", "equanimity"],
        "emotions": ["grief", "anxiety", "confusion"],
        "life_domains": ["grief_loss", "spiritual_practice"],
        "user_intents": ["seeking_peace", "seeking_meaning"],
        "virtues": ["wisdom", "patience", "equanimity"],
        "practice": ["When analysis spirals, stop and rest in not-knowing for one breath cycle."],
        "reflection_question": "Am I grieving a mystery I am trying to force into a small explanation?",
        "related_verses": ["bg_2_24", "bg_2_11", "bg_2_30"],
        "confidence": {"summary": 0.85, "topics": 0.8, "emotions": 0.75, "overall": 0.8},
        "uncertainty_notes": None,
    },
    26: {
        "summary": "Even if you believe the Self is always born and dies, you still should not grieve this way.",
        "modern_interpretation": "Krishna meets you even in alternate worldviews — despair is unnecessary under more than one philosophy of life.",
        "topics": ["wisdom", "equanimity", "grief"],
        "emotions": ["grief", "confusion"],
        "life_domains": ["grief_loss", "spiritual_practice"],
        "user_intents": ["seeking_peace", "seeking_guidance"],
        "virtues": ["patience", "wisdom"],
        "practice": ["Grant that your metaphysics may be incomplete — still choose steadiness today."],
        "reflection_question": "Am I using philosophical uncertainty as permission to stay collapsed?",
        "related_verses": ["bg_2_27", "bg_2_28", "bg_2_11"],
        "confidence": {"summary": 0.8, "topics": 0.7, "emotions": 0.75, "overall": 0.75},
        "uncertainty_notes": "grief is emotion not topic — removed from topics if invalid; using wisdom/equanimity only.",
    },
}


def _fix_26_topics():
    DRAFTS[26]["topics"] = ["wisdom", "equanimity"]


_fix_26_topics()

# Continue drafts 27–72 in second dict merge for readability
DRAFTS.update(
    {
        27: {
            "summary": "Death is certain for the born, and birth for the dead — do not grieve the inevitable.",
            "modern_interpretation": "Facing life's inevitabilities can free energy for love and duty instead of endless bargaining.",
            "topics": ["wisdom", "equanimity", "liberation"],
            "emotions": ["grief", "fear", "anxiety"],
            "life_domains": ["grief_loss", "health", "family"],
            "user_intents": ["seeking_peace", "seeking_courage"],
            "virtues": ["courage", "equanimity", "wisdom"],
            "practice": ["Write one inevitability you resist; practice one gentle acceptance sentence."],
            "reflection_question": "What inevitable truth am I exhausting myself by refusing?",
            "related_verses": ["bg_2_22", "bg_2_28", "bg_2_30"],
            "confidence": {"summary": 0.95, "topics": 0.9, "emotions": 0.85, "overall": 0.9},
            "uncertainty_notes": None,
        },
        28: {
            "summary": "Beings are unmanifest in beginning and end, manifest in the middle — why lament?",
            "modern_interpretation": "Much of life is a brief appearance between mysteries; clinging to the middle chapter as forever creates suffering.",
            "topics": ["wisdom", "equanimity", "detachment"],
            "emotions": ["grief", "anxiety"],
            "life_domains": ["grief_loss", "identity", "spiritual_practice"],
            "user_intents": ["seeking_peace", "seeking_detachment"],
            "virtues": ["wisdom", "non_attachment", "patience"],
            "practice": ["Look at a photo from years ago; feel how forms change while care can continue."],
            "reflection_question": "Where am I demanding permanence from a middle chapter?",
            "related_verses": ["bg_2_27", "bg_2_16", "bg_2_22"],
            "confidence": {"summary": 0.9, "topics": 0.85, "emotions": 0.8, "overall": 0.85},
            "uncertainty_notes": None,
        },
        29: {
            "summary": "Some see the Self as wondrous, some speak of it as wondrous, some hear and never understand.",
            "modern_interpretation": "Deep truth is rare and easily missed — humility beats pretending you already get it.",
            "topics": ["wisdom", "knowledge", "self"],
            "emotions": ["confusion", "awe"],
            "life_domains": ["spiritual_practice", "studies"],
            "user_intents": ["seeking_meaning", "seeking_guidance"],
            "virtues": ["humility", "wisdom", "patience"],
            "practice": ["Admit one spiritual idea you recite but do not yet live."],
            "reflection_question": "Where am I performing understanding instead of patiently learning?",
            "related_verses": ["bg_2_25", "bg_2_16", "bg_2_54"],
            "confidence": {"summary": 0.85, "topics": 0.8, "emotions": 0.6, "overall": 0.75},
            "uncertainty_notes": "awe is not in emotion taxonomy — using confusion; consider adding awe later.",
        },
    }
)

# Fix 29 emotions to taxonomy
DRAFTS[29]["emotions"] = ["confusion", "peace"]

DRAFTS.update(
    {
        30: {
            "summary": "The eternal embodied Self in all bodies cannot be slain — therefore do not grieve for any being.",
            "modern_interpretation": "Compassion remains; hopeless annihilation-fear can loosen when you remember the deeper continuity of being.",
            "topics": ["self", "compassion", "equanimity"],
            "emotions": ["grief", "fear", "peace"],
            "life_domains": ["grief_loss", "family", "spiritual_practice"],
            "user_intents": ["seeking_peace", "seeking_courage"],
            "virtues": ["compassion", "wisdom", "equanimity"],
            "practice": ["Pray or wish well for someone you fear losing — without clinging."],
            "reflection_question": "Can I love someone fully without demanding they be permanent in form?",
            "related_verses": ["bg_2_20", "bg_2_11", "bg_2_27"],
            "confidence": {"summary": 0.9, "topics": 0.85, "emotions": 0.8, "overall": 0.85},
            "uncertainty_notes": None,
        },
        31: {
            "summary": "Considering your own dharma, you should not waver — for a warrior, a righteous battle is the highest good.",
            "modern_interpretation": "Your specific responsibility matters; borrowed ethics that ignore your role can become elegant avoidance.",
            "topics": ["dharma", "duty", "courage"],
            "emotions": ["fear", "confusion", "guilt"],
            "life_domains": ["career", "leadership", "identity"],
            "user_intents": ["seeking_courage", "seeking_guidance"],
            "virtues": ["courage", "discipline", "honesty"],
            "practice": ["Write your role this week in one line; act from that role, not from every opinion."],
            "reflection_question": "What is my dharma here — not my friend's, not the internet's?",
            "related_verses": ["bg_2_33", "bg_2_37", "bg_2_47"],
            "confidence": {"summary": 0.85, "topics": 0.85, "emotions": 0.75, "overall": 0.8},
            "uncertainty_notes": "Warrior dharma needs careful modern translation to vocation/responsibility.",
        },
        32: {
            "summary": "Happy are the warriors who meet such a battle as an open gate to heaven.",
            "modern_interpretation": "A rare, righteous challenge can be a privilege — if faced with integrity rather than bloodlust.",
            "topics": ["dharma", "courage", "duty"],
            "emotions": ["fear", "courage"],
            "life_domains": ["leadership", "career", "identity"],
            "user_intents": ["seeking_courage", "seeking_encouragement"],
            "virtues": ["courage", "discipline"],
            "practice": ["Reframe one hard duty as a rare chance to live your values."],
            "reflection_question": "What difficult opportunity am I treating only as a threat?",
            "related_verses": ["bg_2_31", "bg_2_37", "bg_2_38"],
            "confidence": {"summary": 0.75, "topics": 0.7, "emotions": 0.6, "overall": 0.7},
            "uncertainty_notes": "courage not in emotions taxonomy — using fear + seeking_courage. Heaven language is cultural.",
        },
    }
)
DRAFTS[32]["emotions"] = ["fear", "anxiety"]

# I'll generate remaining verses 33-72 via a compact but specific content table in the runner
# to keep this file maintainable while still verse-specific.
MORE = {
    33: ("Refusing righteous duty brings personal dharma-loss, shame, and harm.", "Avoidance of hard right action often costs integrity more than the confrontation would.", ["dharma", "duty"], ["guilt", "fear", "shame"], ["career", "leadership", "identity"], ["seeking_courage", "seeking_guidance"], ["courage", "honesty"], ["Name the duty you are delaying and the integrity cost of delay."], "What am I losing by not doing what I know is mine to do?", ["bg_2_31", "bg_2_34", "bg_2_47"]),
    34: ("Lasting dishonor is worse than death for one who has been honored.", "Reputation is not vanity alone — trust and self-respect erode when we abandon our post from fear.", ["duty", "dharma", "self"], ["shame", "fear", "anxiety"], ["leadership", "career", "identity"], ["seeking_courage", "seeking_encouragement"], ["courage", "honesty"], ["Ask a mentor what integrity looks like in your situation — not what is easiest."], "Am I protecting comfort at the price of becoming untrustworthy to myself?", ["bg_2_33", "bg_2_35", "bg_2_36"]),
    35: ("Great peers will think you withdrew from battle out of fear.", "People read our withdrawals; sometimes fear masquerades as principle.", ["duty", "courage", "mind"], ["shame", "fear"], ["leadership", "career", "relationships"], ["seeking_courage"], ["courage", "honesty"], ["Distinguish principle from fear by asking what you would do if nobody watched."], "If reputation were irrelevant, would my choice stay the same?", ["bg_2_34", "bg_2_36", "bg_2_3"]),
    36: ("Enemies will mock your strength with cruel words — what could be more painful?", "Public scorn hurts; wisdom still asks whether the scorn is deserved or merely loud.", ["mind", "duty", "courage"], ["shame", "anger", "anxiety"], ["leadership", "career", "relationships"], ["seeking_courage", "seeking_peace"], ["patience", "courage", "equanimity"], ["Do not answer mockery today; strengthen your next right action instead."], "Whose opinion is wounding me — and do they deserve that much power?", ["bg_2_34", "bg_2_35", "bg_2_38"]),
    37: ("Slain, you gain heaven; victorious, you enjoy the earth — therefore rise with resolve.", "Either path of sincere duty can be lived with dignity; indecision is the true loss.", ["duty", "courage", "dharma"], ["fear", "anxiety"], ["career", "leadership", "identity"], ["seeking_courage", "seeking_encouragement"], ["courage", "discipline", "perseverance"], ["Choose the next courageous action and schedule it within 24 hours."], "What decision am I postponing that both outcomes could honor if done cleanly?", ["bg_2_3", "bg_2_31", "bg_2_38"]),
    38: ("Treat pleasure-pain, gain-loss, victory-defeat alike — then act without accruing harm.", "Equanimity is the ethical technology that lets you act without becoming cruel or collapsed.", ["equanimity", "duty", "yoga"], ["anxiety", "fear", "anger"], ["career", "leadership", "spiritual_practice"], ["seeking_peace", "seeking_discipline"], ["equanimity", "discipline", "non_attachment"], ["Before a high-stakes moment, name win and lose as equal teachers."], "Can I act fully without needing the scoreboard to justify me?", ["bg_2_14", "bg_2_48", "bg_2_56"]),
    39: ("This is the wisdom of Sankhya; now hear the yoga of buddhi by which you free yourself from bondage.", "Philosophy becomes liberating when it turns into a lived discipline of intelligent action.", ["wisdom", "yoga", "karma"], ["confusion", "hope"], ["spiritual_practice", "studies", "career"], ["seeking_guidance", "seeking_meaning"], ["wisdom", "discipline"], ["Shift from 'what is true?' alone to 'how shall I act on what is true?'"], "Where do I understand more than I practice?", ["bg_2_40", "bg_2_47", "bg_2_50"]),
    40: ("On this path no effort is lost, no harm accrues; even a little of this dharma protects from great fear.", "Small sincere practice compounds; you do not need a perfect spiritual career to begin.", ["dharma", "yoga", "discipline"], ["fear", "anxiety", "hopelessness"], ["spiritual_practice", "career", "studies"], ["seeking_encouragement", "seeking_discipline"], ["perseverance", "discipline", "courage"], ["Do five minutes of sincere practice today — count it as real."], "What small practice have I dismissed because it was not dramatic enough?", ["bg_2_41", "bg_2_48", "bg_2_50"]),
    41: ("Resolute understanding is single-pointed; the irresolute have many-branched endless thoughts.", "Scattered motivation feels busy; committed intention feels simple and strong.", ["mind", "discipline", "wisdom"], ["anxiety", "restlessness", "confusion"], ["career", "studies", "spiritual_practice"], ["seeking_discipline", "seeking_peace"], ["discipline", "perseverance", "self_control"], ["Choose one aim for this week and cut two distractions that dilute it."], "Where is my energy leaking into a hundred half-decisions?", ["bg_2_40", "bg_2_44", "bg_2_53"]),
    42: ("The unwise cling to flowery Vedic promises and say there is nothing more.", "Spiritual consumerism chases rewards and misses the deeper work of transformation.", ["desire", "wisdom", "knowledge"], ["confusion", "restlessness"], ["spiritual_practice", "money", "identity"], ["seeking_meaning", "seeking_detachment"], ["wisdom", "non_attachment", "honesty"], ["Notice one 'spiritual' goal that is actually a luxury fantasy."], "Am I seeking truth — or a more impressive consolation prize?", ["bg_2_43", "bg_2_44", "bg_2_45"]),
    43: ("Desire-driven people pursue heaven through elaborate rites aimed at pleasure and power.", "Complex self-improvement can still be ego in sacred costume if pleasure and status remain the gods.", ["desire", "karma", "renunciation"], ["restlessness", "anxiety"], ["spiritual_practice", "career", "money"], ["seeking_detachment", "seeking_meaning"], ["non_attachment", "honesty", "discipline"], ["Fast from one status metric for a week (likes, rank, salary talk)."], "Which spiritual effort is secretly about looking successful?", ["bg_2_42", "bg_2_44", "bg_2_49"]),
    44: ("Those attached to pleasure and power cannot form resolute buddhi for samadhi.", "Attachment fragments attention; deep focus needs a quieter hunger.", ["desire", "mind", "discipline"], ["restlessness", "anxiety", "overwhelm"], ["career", "money", "spiritual_practice"], ["seeking_discipline", "seeking_detachment"], ["self_control", "discipline", "non_attachment"], ["Silence notifications during your deepest work block today."], "What pleasure or power chase is stealing my capacity for depth?", ["bg_2_41", "bg_2_43", "bg_2_62"]),
    45: ("The Vedas deal with the three gunas; rise beyond them — free of dualities, established in sattva, free of grasping.", "Grow past mood-driven living; seek a steadier center than preference and aversion.", ["equanimity", "wisdom", "detachment"], ["restlessness", "anxiety", "anger"], ["spiritual_practice", "identity", "health"], ["seeking_detachment", "seeking_peace"], ["equanimity", "non_attachment", "self_control"], ["When pulled by like/dislike, name the guna-mood and choose one neutral action."], "Where am I ruled by preference rather than purpose?", ["bg_2_38", "bg_2_48", "bg_2_56"]),
    46: ("As a flood makes a well unnecessary, so the knower of Brahman needs little of Vedic ritual reward.", "When you taste a deeper fullness, compulsive spiritual shopping loosens.", ["wisdom", "liberation", "knowledge"], ["anxiety", "peace"], ["spiritual_practice", "identity"], ["seeking_meaning", "seeking_peace"], ["wisdom", "non_attachment"], ["Replace one outer spiritual consumption with ten minutes of quiet insight."], "What am I still collecting because I have not yet trusted inner fullness?", ["bg_2_45", "bg_2_52", "bg_2_55"]),
    47: ("You have a right to action alone, never to its fruits — do not cause results, and do not cling to inaction.", "Do the work; release the outcome; do not use detachment as laziness. Perfectionism often hides in fruit-obsession.", ["duty", "karma", "detachment"], ["anxiety", "fear"], ["career", "placements", "business"], ["seeking_guidance", "seeking_encouragement", "seeking_detachment"], ["discipline", "perseverance", "non_attachment"], ["Focus on today's work.", "Do not obsess over outcomes."], "Where am I attaching my happiness to the outcome — and calling it high standards?", ["bg_2_48", "bg_2_49", "bg_2_50"]),
    48: ("Established in yoga, act; abandon attachment; be even in success and failure — that evenness is yoga.", "Yoga here is composure in motion, not escape from work.", ["yoga", "equanimity", "duty", "detachment"], ["anxiety", "fear", "restlessness"], ["career", "studies", "leadership"], ["seeking_peace", "seeking_discipline", "seeking_courage"], ["equanimity", "discipline", "patience"], ["Before a result arrives, name one action still fully in your control."], "Can I stay kind and clear whether this attempt succeeds or fails?", ["bg_2_47", "bg_2_50", "bg_2_38"]),
    49: ("Far inferior is reward-driven action; take refuge in buddhi-yoga — fruit-seekers are spiritually impoverished.", "When payoff is the only motive, work shrinks the heart.", ["karma", "wisdom", "detachment", "action"], ["anxiety", "guilt", "confusion"], ["career", "money", "business"], ["seeking_meaning", "seeking_guidance", "seeking_detachment"], ["wisdom", "non_attachment", "honesty"], ["Write the purpose of your work beyond salary or status."], "Where has chasing reward made my work smaller than it could be?", ["bg_2_47", "bg_2_50", "bg_2_51"]),
    50: ("One yoked to buddhi casts off good and bad reactions here; therefore devote yourself to yoga — yoga is skill in action.", "Skill in action is excellence with a clear mind, not clever hustling for credit.", ["yoga", "wisdom", "action", "discipline"], ["anxiety", "overwhelm", "peace"], ["career", "studies", "leadership", "spiritual_practice"], ["seeking_discipline", "seeking_courage", "seeking_peace"], ["discipline", "wisdom", "perseverance"], ["Choose one task and do it with full attention for twenty minutes."], "What would 'skill in action' look like in my hardest task this week?", ["bg_2_47", "bg_2_48", "bg_2_49"]),
    51: ("The wise, abandoning the fruit born of action, freed from birth-bondage, reach the painless state.", "Release the harvest obsession and a quieter freedom becomes possible.", ["karma", "detachment", "liberation"], ["anxiety", "peace"], ["spiritual_practice", "career"], ["seeking_detachment", "seeking_peace"], ["non_attachment", "wisdom"], ["After finishing work, consciously hand the result over — then stop refreshing for updates."], "What fruit am I gripping so tightly that I cannot rest?", ["bg_2_47", "bg_2_50", "bg_2_71"]),
    52: ("When your buddhi crosses the thicket of delusion, you become indifferent to what is heard and yet to be heard.", "Clarity reduces craving for endless opinions and hot takes.", ["wisdom", "mind", "detachment"], ["confusion", "restlessness", "anxiety"], ["studies", "spiritual_practice", "career"], ["seeking_peace", "seeking_detachment"], ["wisdom", "non_attachment", "self_control"], ["Take a 24-hour fast from advice-content; trust one clear principle instead."], "Which noise am I consuming because I am afraid to decide?", ["bg_2_53", "bg_2_41", "bg_2_45"]),
    53: ("When buddhi, bewildered by conflicting scriptures, stands unmoved in samadhi — then you attain yoga.", "Yoga ripens when attention stops thrashing between contradictory voices.", ["yoga", "mind", "wisdom"], ["confusion", "anxiety", "peace"], ["spiritual_practice", "studies"], ["seeking_peace", "seeking_discipline"], ["discipline", "equanimity", "wisdom"], ["Pick one practice and stay with it for seven days without switching systems."], "What conflicting advice is keeping my mind from settling?", ["bg_2_52", "bg_2_48", "bg_2_54"]),
    54: ("Arjuna asks: how does one of steady wisdom speak, sit, and walk?", "We recognize awakening not by slogans but by how a person moves through ordinary life.", ["wisdom", "mind", "discipline"], ["curiosity", "confusion"], ["spiritual_practice", "identity"], ["seeking_guidance", "seeking_meaning"], ["humility", "wisdom"], ["Observe one calm person today; note concrete behaviors, not aura myths."], "What lived signs of steadiness am I actually looking for?", ["bg_2_55", "bg_2_56", "bg_2_57"]),
}


def _pack(verse: int, row: tuple) -> dict:
    (
        summary,
        modern,
        topics,
        emotions,
        domains,
        intents,
        virtues,
        practice,
        reflection,
        related,
    ) = row
    # normalize practice to list
    practices = practice if isinstance(practice, list) else [practice]
    # filter invalid emotion curiosity
    emo = [e for e in emotions if e != "curiosity"]
    if "curiosity" in emotions and "confusion" not in emo:
        emo.append("confusion")
    return {
        "summary": summary,
        "modern_interpretation": modern,
        "topics": topics,
        "emotions": emo,
        "life_domains": domains,
        "user_intents": intents,
        "virtues": virtues,
        "practice": practices,
        "reflection_question": reflection,
        "related_verses": related,
        "confidence": {
            "summary": 0.85,
            "topics": 0.8,
            "emotions": 0.75,
            "overall": 0.8,
        },
        "uncertainty_notes": "Draft enrichment for human review; not auto-approved.",
    }


for v, row in MORE.items():
    DRAFTS[v] = _pack(v, row)

# Verses 55–72
FINAL = {
    55: ("Steady wisdom is when one abandons desires of the mind and rests content in the Self alone.", "Inner fullness beats endless wanting; contentment is a skill, not a mood.", ["desire", "self", "wisdom"], ["restlessness", "anxiety", "peace"], ["spiritual_practice", "identity"], ["seeking_peace", "seeking_detachment"], ["non_attachment", "wisdom", "self_control"], ["List three desires; release chasing one of them today on purpose."], "What desire is running my mind without my consent?", ["bg_2_54", "bg_2_56", "bg_2_71"]),
    56: ("Unshaken in sorrow, without craving in joy, free of attachment, fear, and anger — that sage is steady in wisdom.", "Emotional adulthood is freedom from being yanked by every high and low.", ["equanimity", "mind", "wisdom"], ["anger", "fear", "anxiety", "peace"], ["relationships", "career", "spiritual_practice"], ["seeking_peace", "seeking_discipline"], ["equanimity", "patience", "self_control"], ["In the next mood swing, delay reaction by ninety seconds."], "Which emotion currently has the authority to drive my decisions?", ["bg_2_55", "bg_2_57", "bg_2_64"]),
    57: ("Who is unattached everywhere, neither rejoicing nor hating good or bad fortune — that one's wisdom is firm.", "Favorable and unfavorable events need not own your inner climate.", ["equanimity", "detachment", "wisdom"], ["anger", "anxiety", "peace"], ["career", "relationships", "leadership"], ["seeking_detachment", "seeking_peace"], ["equanimity", "non_attachment"], ["Receive one piece of good and bad news today with the same paced breath."], "Where do I still need the world to behave before I allow myself steadiness?", ["bg_2_56", "bg_2_38", "bg_2_48"]),
    58: ("When one withdraws the senses from objects as a tortoise draws in its limbs — wisdom is firm.", "Healthy withdrawal is skillful boundaries, not lifelong escape.", ["mind", "discipline", "wisdom"], ["restlessness", "overwhelm", "anxiety"], ["spiritual_practice", "health", "studies"], ["seeking_discipline", "seeking_peace"], ["self_control", "discipline", "patience"], ["Create one tortoise move today: withdraw from a draining feed for an evening."], "What sense-input do I need to pull back from to recover clarity?", ["bg_2_59", "bg_2_60", "bg_2_68"]),
    59: ("Objects turn away from the abstainer, but taste remains; even taste turns away after seeing the Supreme.", "Willpower can pause habits; deeper fulfillment dissolves the craving itself.", ["desire", "discipline", "liberation"], ["restlessness", "anxiety"], ["spiritual_practice", "health"], ["seeking_discipline", "seeking_detachment"], ["self_control", "perseverance", "wisdom"], ["Abstain from one craving and also cultivate one deeper joy (walk, prayer, music)."], "Am I only suppressing a craving — or replacing it with deeper nourishment?", ["bg_2_58", "bg_2_60", "bg_2_70"]),
    60: ("Even a wise striving person's turbulent senses can forcibly carry away the mind.", "Insight does not make you immune; vigilance remains part of maturity.", ["mind", "discipline", "desire"], ["restlessness", "anxiety", "overwhelm"], ["spiritual_practice", "health", "relationships"], ["seeking_discipline", "seeking_courage"], ["humility", "self_control", "perseverance"], ["Expect setbacks; plan a gentle restart ritual after a slip."], "Where do I pretend I am beyond temptation?", ["bg_2_59", "bg_2_61", "bg_2_67"]),
    61: ("Restraining all senses, sit devoted to the Divine; one whose senses are mastered has firm wisdom.", "Mastery of attention is devotion in daily form.", ["discipline", "devotion", "mind"], ["restlessness", "anxiety", "peace"], ["spiritual_practice", "studies"], ["seeking_discipline", "seeking_peace"], ["self_control", "devotion", "discipline"], ["Begin work with one minute of dedication — then single-task."], "What would sense-mastery look like on my phone and calendar?", ["bg_2_60", "bg_2_68", "bg_2_58"]),
    62: ("Dwelling on sense objects breeds attachment; attachment breeds desire; desire breeds anger.", "The spiral from rumination to rage is predictable — interrupt earlier.", ["mind", "desire", "anger"], ["anger", "restlessness", "anxiety"], ["relationships", "career", "health"], ["seeking_discipline", "seeking_peace"], ["self_control", "patience", "wisdom"], ["When obsessing on an object/person/outcome, name the chain: dwell → attach → crave."], "What am I repeatedly dwelling on that is quietly building anger?", ["bg_2_63", "bg_2_64", "bg_2_44"]),
    63: ("From anger comes delusion; from delusion, memory failure; from that, buddhi dies — and one falls.", "Anger is not just heat; it is a cognitive blackout waiting to happen.", ["anger", "mind", "wisdom"], ["anger", "confusion", "overwhelm"], ["relationships", "family", "career"], ["seeking_peace", "seeking_discipline", "seeking_forgiveness"], ["patience", "self_control", "wisdom"], ["Use a cool-down script: leave the room, drink water, write the angry sentence privately."], "Where has anger already started erasing my memory of what matters?", ["bg_2_62", "bg_2_64", "bg_2_56"]),
    64: ("Moving among objects with senses free of attraction and aversion, self-governed — one attains serenity.", "Engagement without compulsion is freedom in the middle of ordinary life.", ["equanimity", "discipline", "mind"], ["restlessness", "anger", "peace"], ["relationships", "career", "spiritual_practice"], ["seeking_peace", "seeking_detachment"], ["self_control", "equanimity", "non_attachment"], ["Participate fully in one enjoyable thing without needing more afterward."], "Can I enjoy without grasping and face dislike without hostility?", ["bg_2_63", "bg_2_65", "bg_2_57"]),
    65: ("In that serenity, all sorrows cease; the buddhi of a serene mind soon becomes steady.", "Calm is not cosmetic — it restores intelligence.", ["peace", "mind", "wisdom"], ["peace", "anxiety", "grief"], ["health", "spiritual_practice", "career"], ["seeking_peace", "seeking_encouragement"], ["equanimity", "patience", "wisdom"], ["Protect a daily serenity block as seriously as a meeting."], "What sorrow softens when my mind is even slightly more serene?", ["bg_2_64", "bg_2_66", "bg_2_70"]),
    66: ("There is no buddhi for the unyoked, nor meditation, nor peace — and without peace, how can there be happiness?", "Happiness is downstream of inner alignment; chaos cannot deliver it.", ["mind", "yoga", "peace"], ["anxiety", "restlessness", "hopelessness"], ["spiritual_practice", "health", "career"], ["seeking_peace", "seeking_discipline"], ["discipline", "wisdom", "patience"], ["Before seeking a mood boost, restore one alignment: sleep, prayer, or honest conversation."], "Am I chasing happiness while refusing the peace that makes it possible?", ["bg_2_65", "bg_2_67", "bg_2_71"]),
    67: ("As wind carries away a boat, the mind that follows wandering senses steals one's wisdom.", "Attention is the rudder; wherever it goes, your life follows.", ["mind", "discipline", "wisdom"], ["restlessness", "overwhelm", "anxiety"], ["studies", "career", "spiritual_practice"], ["seeking_discipline", "seeking_peace"], ["self_control", "discipline"], ["Choose a single 'rudder object' for the next hour and refuse tab-hopping."], "What wind is currently steering my mind away from wisdom?", ["bg_2_60", "bg_2_66", "bg_2_68"]),
    68: ("Therefore, one whose senses are fully restrained from their objects has firm wisdom.", "Boundary is the architecture of clarity.", ["discipline", "mind", "wisdom"], ["restlessness", "anxiety", "peace"], ["spiritual_practice", "studies", "health"], ["seeking_discipline", "seeking_peace"], ["self_control", "discipline", "perseverance"], ["Set one hard boundary tonight (time, app, or conversation) and keep it."], "Which unrestrained sense habit most destabilizes my judgment?", ["bg_2_58", "bg_2_61", "bg_2_67"]),
    69: ("What is night for all beings is waking for the disciplined; what is waking for beings is night for the sage.", "Values invert as wisdom deepens — noise looks like sleep, and stillness looks like life.", ["wisdom", "discipline", "mind"], ["restlessness", "peace"], ["spiritual_practice", "identity"], ["seeking_meaning", "seeking_peace"], ["wisdom", "discipline", "non_attachment"], ["Spend thirty minutes in the 'night of the world' (quiet) and notice what awakens."], "Where do I still call distraction 'living' and stillness 'missing out'?", ["bg_2_68", "bg_2_70", "bg_2_71"]),
    70: ("As rivers enter a full ocean without disturbing it, desires enter one who is steady — that one attains peace.", "Peace is not empty of desire; it is spacious enough not to be overturned by desire.", ["desire", "peace", "equanimity"], ["restlessness", "anxiety", "peace"], ["spiritual_practice", "career", "relationships"], ["seeking_peace", "seeking_detachment"], ["equanimity", "non_attachment", "patience"], ["Let a desire arise and pass like a river; do not build a dam of obsession."], "Which desire is currently flooding my inner shoreline?", ["bg_2_71", "bg_2_55", "bg_2_65"]),
    71: ("Abandoning all desires, moving free of longing, without mine-making or ego — one attains peace.", "Peace ripens when ownership-compulsion and self-importance loosen.", ["desire", "detachment", "liberation"], ["anxiety", "peace"], ["spiritual_practice", "identity", "relationships"], ["seeking_peace", "seeking_detachment"], ["non_attachment", "humility", "peace"], ["Notice one 'mine' thought today and soften it: this is entrusted, not owned."], "Where is 'I / mine' creating unnecessary tension?", ["bg_2_70", "bg_2_55", "bg_2_72"]),
    72: ("This is the Brahmi state; attaining it, one is not deluded, and at life's end reaches Brahman-nirvana.", "A life trained in steadiness culminates in freedom — practice now is preparation for the last breath too.", ["liberation", "wisdom", "equanimity"], ["peace", "fear", "anxiety"], ["spiritual_practice", "grief_loss", "identity"], ["seeking_peace", "seeking_meaning"], ["wisdom", "equanimity", "devotion"], ["Ask: if today were late in life, what steadiness would I wish I had practiced?"], "What state of mind am I rehearsing for my final moments by how I live today?", ["bg_2_71", "bg_2_55", "bg_2_50"]),
}

for v, row in FINAL.items():
    DRAFTS[v] = _pack(v, row)

# Fix taxonomy issues
DRAFTS[39]["emotions"] = ["confusion", "peace"]  # hope -> peace
DRAFTS[65]["topics"] = ["mind", "wisdom", "equanimity"]  # peace not a topic
DRAFTS[66]["topics"] = ["mind", "yoga", "equanimity"]
DRAFTS[70]["topics"] = ["desire", "equanimity", "liberation"]
DRAFTS[71]["virtues"] = ["non_attachment", "humility", "equanimity"]  # peace not virtue


def main() -> None:
    missing = [i for i in range(1, 73) if i not in DRAFTS]
    if missing:
        raise SystemExit(f"Missing drafts for verses: {missing}")

    enrichments = []
    for verse in range(1, 73):
        d = DRAFTS[verse]
        enrichments.append(
            {
                "node_id": f"bg_2_{verse}",
                "citation": f"BG 2.{verse}",
                "status": "draft",
                "summary": d["summary"],
                "modern_interpretation": d["modern_interpretation"],
                "topics": d["topics"],
                "emotions": d["emotions"],
                "life_domains": d["life_domains"],
                "user_intents": d["user_intents"],
                "virtues": d["virtues"],
                "practice": d["practice"],
                "reflection_question": d["reflection_question"],
                "related_verses": d["related_verses"],
                "confidence": d["confidence"],
                "uncertainty_notes": d.get("uncertainty_notes"),
                "reviewed_by": None,
                "approved_at": None,
            }
        )

    document = {
        "manifest": {
            "name": "Sarathi Intelligence",
            "scripture": "bhagavad_gita",
            "chapter": 2,
            "version": "0.1.0-draft",
            "status": "draft",
            "authentic_corpus": "../bhagavad_gita.json",
            "description": (
                "Human-reviewable Sarathi Intelligence overlays for Chapter 2. "
                "Does not modify Authentic Scripture. Nothing here is approved until reviewed."
            ),
            "enrichment_count": len(enrichments),
            "approval_policy": "draft → review → approve → lock; never auto-approve",
        },
        "enrichments": enrichments,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"enrichments {len(enrichments)} status=draft")


if __name__ == "__main__":
    main()
