#!/bin/bash
# Cleanup script for AI Plan Generation project
# This script lists files that can be safely removed

echo "=================================================="
echo "AI Plan Generation - File Cleanup"
echo "=================================================="
echo ""

echo "📦 CORE FILES (KEEP - needed for backend integration):"
echo "  Services:"
echo "    - openai_service.py"
echo "    - ai_plan_generation_service.py"
echo "    - constraint_parser.py"
echo "    - exercise_selector.py"
echo "    - cardio_selector.py"
echo ""
echo "  Repositories:"
echo "    - exercise_reference_repository.py"
echo "    - exercise_standard_repository.py"
echo "    - cardio_reference_repository.py"
echo ""
echo "  Models:"
echo "    - base.py"
echo "    - exercise_reference.py"
echo "    - exercise_standard.py"
echo "    - cardio_reference.py"
echo ""
echo "  Config:"
echo "    - config.py"
echo "    - requirements.txt"
echo "    - .env"
echo ""
echo "  Temporary (until cardio in DB):"
echo "    - mock_cardio_database.py"
echo ""

echo "🧪 TEST FILES (KEEP for development):"
echo "    - test_plan_generation_clean.py (main test suite)"
echo "    - test_my_custom_plan.py (optional - interactive testing)"
echo ""

echo "🗑️  FILES TO DELETE:"
echo ""
echo "  Deprecated/Unused:"
echo "    - mock_database.py (not used)"
echo "    - cardio_templates.py (replaced by cardio database)"
echo "    - workout_plan_service.py (old template system)"
echo ""

echo "  Redundant Test Files:"
echo "    - test_openai_direct.py"
echo "    - test_with_real_db.py"
echo "    - test_constraint_openai.py"
echo "    - test_constraint_check.py"
echo "    - test_older_beginner.py"
echo "    - test_young_advanced.py"
echo "    - test_plan_generation.py"
echo "    - test_exercise_db_simple.py"
echo "    - test_weight_loss.py"
echo "    - test_age_experience_adaptation.py"
echo "    - test_constraint_parser.py"
echo "    - interactive_test.py"
echo ""

echo "  Generated Output Files:"
echo "    - test_plan_output.json"
echo "    - test_plan_real_db.json"
echo "    - test_plan_older_beginner.json"
echo "    - test_plan_young_advanced.json"
echo "    - my_custom_plan.json"
echo "    - workout_plan.md"
echo "    - test_output_basic.json"
echo "    - test_output_abs_leg_days.json"
echo "    - test_output_equipment.json"
echo "    - test_output_older_beginner.json"
echo ""

echo "  Documentation (consolidate to CORE_FILES.md):"
echo "    - README_AI_INTEGRATION.md"
echo "    - IMPLEMENTATION_SUMMARY.md"
echo "    - QUICK_START.md"
echo "    - FILE_LIST.md"
echo "    - INTERACTIVE_TEST_GUIDE.md"
echo "    - WEIGHT_INTEGRATION_STATUS.md"
echo "    - USER_PREFERENCES_NOTE.md"
echo ""

echo "=================================================="
echo "Would you like to delete these files? (y/n)"
read -r response

if [[ "$response" == "y" ]]; then
    echo ""
    echo "Deleting deprecated files..."
    
    # Remove deprecated code
    rm -f mock_database.py cardio_templates.py workout_plan_service.py
    
    # Remove redundant tests
    rm -f test_openai_direct.py test_with_real_db.py test_constraint_openai.py \
          test_constraint_check.py test_older_beginner.py test_young_advanced.py \
          test_plan_generation.py test_exercise_db_simple.py test_weight_loss.py \
          test_age_experience_adaptation.py test_constraint_parser.py interactive_test.py
    
    # Remove generated outputs
    rm -f test_plan_output.json test_plan_real_db.json test_plan_older_beginner.json \
          test_plan_young_advanced.json my_custom_plan.json workout_plan.md \
          test_output_basic.json test_output_abs_leg_days.json test_output_equipment.json \
          test_output_older_beginner.json
    
    # Remove old docs
    rm -f README_AI_INTEGRATION.md IMPLEMENTATION_SUMMARY.md QUICK_START.md \
          FILE_LIST.md INTERACTIVE_TEST_GUIDE.md WEIGHT_INTEGRATION_STATUS.md \
          USER_PREFERENCES_NOTE.md
    
    echo "✅ Cleanup complete!"
    echo ""
    echo "Remaining structure:"
    ls -1 *.py *.md 2>/dev/null
else
    echo "Cleanup cancelled."
fi
