import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.evaluation_service import evaluation_service

def test_question_score_formula():
    # Formula: 0.30*Tech + 0.20*Corr + 0.15*Comp + 0.15*Relev + 0.20*Comm
    tech = 8.0
    corr = 9.0
    comp = 7.0
    relev = 9.0
    comm = 8.0

    expected = (0.30 * 8.0) + (0.20 * 9.0) + (0.15 * 7.0) + (0.15 * 9.0) + (0.20 * 8.0)
    # 2.4 + 1.8 + 1.05 + 1.35 + 1.6 = 8.2

    actual = evaluation_service.calculate_question_score(
        correctness=corr,
        relevance=relev,
        completeness=comp,
        technical_understanding=tech,
        communication=comm
    )
    assert actual == round(expected, 2)
    assert actual == 8.2
