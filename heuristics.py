# heuristics.py

NIELSEN_HEURISTICS = [
    {
        "id": 1,
        "name": "Visibility of System Status",
        "desc": "Keep users informed about what is going on through appropriate feedback within reasonable time.",
        "questions": [
            "Does the interface provide timely feedback after user actions?",
            "Are system states (loading, saving, errors) clearly indicated?",
            "Do users always know what the system is doing?"
        ],
        "fairness": "Could users with slow devices, low vision, or color-blindness miss important feedback cues?"
    },
    {
        "id": 2,
        "name": "Match Between System and the Real World",
        "desc": "The system should speak the users’ language, using familiar concepts and following real-world conventions.",
        "questions": [
            "Does the interface use familiar words, symbols, or metaphors?",
            "Are icons or labels meaningful for the intended audience?",
            "Is the information order consistent with real-world logic?"
        ],
        "fairness": "Could cultural or linguistic differences make terminology confusing or exclusionary?"
    },
    {
        "id": 3,
        "name": "User Control and Freedom",
        "desc": "Users often choose system functions by mistake and need a clearly marked 'emergency exit' to leave unwanted states.",
        "questions": [
            "Can users easily undo or redo actions?",
            "Are there clear ways to exit or cancel operations?",
            "Does the system prevent users from getting stuck?"
        ],
        "fairness": "Could novice users or people with motor impairments find it difficult to undo mistakes?"
    },
    {
        "id": 4,
        "name": "Consistency and Standards",
        "desc": "Users should not have to wonder whether different words, situations, or actions mean the same thing.",
        "questions": [
            "Are terminology and layout consistent across screens?",
            "Do buttons and icons behave predictably?",
            "Is there alignment with common platform conventions?"
        ],
        "fairness": "Could inconsistent patterns confuse non-native speakers or neurodiverse users?"
    },
    {
        "id": 5,
        "name": "Error Prevention",
        "desc": "Designs should prevent problems from occurring in the first place rather than relying on error messages.",
        "questions": [
            "Does the system prevent invalid input or accidental submission?",
            "Are confirmation dialogs provided for critical actions?",
            "Are risky operations clearly differentiated from safe ones?"
        ],
        "fairness": "Could some users (e.g., low literacy or low vision) be more prone to triggering preventable errors?"
    },
    {
        "id": 6,
        "name": "Recognition Rather Than Recall",
        "desc": "Minimize users’ memory load by making options and instructions visible.",
        "questions": [
            "Are options, menus, or recent actions visible instead of hidden?",
            "Is it easy to find information without remembering previous steps?",
            "Are cues provided for incomplete tasks or actions?"
        ],
        "fairness": "Could users with cognitive or memory difficulties struggle if too much relies on recall?"
    },
    {
        "id": 7,
        "name": "Flexibility and Efficiency of Use",
        "desc": "Accelerators—unseen by the novice user—may speed up interaction for expert users while remaining simple for beginners.",
        "questions": [
            "Does the system support both novice and expert workflows?",
            "Are there shortcuts or customization options?",
            "Is efficiency balanced with clarity?"
        ],
        "fairness": "Could efficiency features favor advanced users and leave novices disadvantaged?"
    },
    {
        "id": 8,
        "name": "Aesthetic and Minimalist Design",
        "desc": "Interfaces should not contain information that is irrelevant or rarely needed.",
        "questions": [
            "Is the layout uncluttered and easy to scan?",
            "Does every element serve a clear purpose?",
            "Are color and typography used consistently?"
        ],
        "fairness": "Could minimalism reduce accessibility (e.g., low contrast, small text) for certain users?"
    },
    {
        "id": 9,
        "name": "Help Users Recognize, Diagnose, and Recover from Errors",
        "desc": "Error messages should be expressed in plain language, precisely indicate the problem, and suggest a solution.",
        "questions": [
            "Are error messages clear, polite, and specific?",
            "Do they suggest corrective actions?",
            "Are errors easily recoverable?"
        ],
        "fairness": "Could certain users (e.g., non-native speakers) find error messages confusing or unhelpful?"
    },
    {
        "id": 10,
        "name": "Help and Documentation",
        "desc": "Even though it is better if the system can be used without documentation, it may be necessary to provide help.",
        "questions": [
            "Is help content easy to find and contextually relevant?",
            "Are examples or visuals provided for complex features?",
            "Is support accessible for different user abilities?"
        ],
        "fairness": "Could documentation exclude certain groups (e.g., low literacy, screen reader users) if not made accessible?"
    }
]
