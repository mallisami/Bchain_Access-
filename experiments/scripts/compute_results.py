import csv
import math
import os
import sys

def load_csv(filepath):
    data = []
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found.", file=sys.stderr)
        return data
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Try to convert values to numeric where appropriate
            typed_row = {}
            for k, v in row.items():
                try:
                    if "." in v:
                        typed_row[k] = float(v)
                    else:
                        typed_row[k] = int(v)
                except ValueError:
                    typed_row[k] = v
            data.append(typed_row)
    return data

def calc_mean_sd(values):
    n = len(values)
    if n == 0:
        return 0.0, 0.0
    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / (n - 1) if n > 1 else 0.0
    sd = math.sqrt(variance)
    return mean, sd

def calc_95_ci_t(values):
    n = len(values)
    if n < 2:
        return 0.0, 0.0
    mean, sd = calc_mean_sd(values)
    # Critical t-value for 95% CI (two-tailed)
    # N=10 (df=9): 2.262157
    t_table = {
        1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
        6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
        15: 2.131, 20: 2.086, 30: 2.042, 60: 2.000, 120: 1.980
    }
    df = n - 1
    t_crit = t_table.get(df, 1.960 if df > 120 else 2.262) # fallback to t-distribution or z
    std_err = sd / math.sqrt(n)
    margin = t_crit * std_err
    return mean - margin, mean + margin

def map_sus_adjective(score):
    # Bangor et al. (2008) / Brooke (1996) mapping
    if score >= 85.0:
        return "Excellent", "Grade A", "Acceptable"
    elif score >= 71.0:
        return "Good", "Grade B", "Acceptable"
    elif score >= 50.0:
        return "OK", "Grade D", "Marginal"
    else:
        return "Poor", "Grade F", "Unacceptable"

def main():
    print("======================================================================")
    print("      BCHAIN-ACCESS EXPERT EVALUATION RESULTS REPRODUCTION SCRIPT     ")
    print("======================================================================\n")

    # Paths
    sus_path = "data/sus_scores.csv"
    cw_path = "data/cognitive_walkthrough.csv"
    aq_path = "data/accessibility_questionnaire.csv"
    he_path = "data/heuristic_ratings.csv"

    # 1. SUS ANALYSIS
    print("--- 1. SYSTEM USABILITY SCALE (SUS) ANALYSIS ---")
    sus_data = load_csv(sus_path)
    if sus_data:
        scores = [row["SUSScore"] for row in sus_data]
        mean, sd = calc_mean_sd(scores)
        ci_lower, ci_upper = calc_95_ci_t(scores)
        
        print(f"Total Evaluators (N): {len(scores)}")
        print(f"Mean SUS Score:       {mean:.2f} (Paper reports: 87.5)")
        print(f"Standard Deviation:   {sd:.2f} (Paper reports: 5.27)")
        print(f"Minimum SUS Score:    {min(scores):.1f}")
        print(f"Maximum SUS Score:    {max(scores):.1f}")
        print(f"95% Confidence Int.:  [{ci_lower:.2f}, {ci_upper:.2f}] (t-distribution, df={len(scores)-1})")
        
        overall_adj, overall_grade, overall_acc = map_sus_adjective(mean)
        print(f"Adjective Rating:     {overall_adj}")
        print(f"Grade Scale:          {overall_grade}")
        print(f"Acceptability:        {overall_acc}\n")
        
        print("Per-Evaluator SUS Summary:")
        print(f"{'Evaluator':<12} | {'Score':<6} | {'Adjective':<10} | {'Grade':<8} | {'Acceptability':<12}")
        print("-" * 59)
        for row in sus_data:
            eid = row["EvaluatorID"]
            score = row["SUSScore"]
            adj, grade, acc = map_sus_adjective(score)
            print(f"{eid:<12} | {score:<6.1f} | {adj:<10} | {grade:<8} | {acc:<12}")
        print()
    else:
        print("No SUS data found.\n")

    # 2. EXPERT TASK-WORKBOOK DESCRIPTIVE ANALYSIS
    print("--- 2. EXPERT TASK-WORKBOOK DESCRIPTIVE ANALYSIS ---")
    cw_data = load_csv(cw_path)
    if cw_data:
        # Group recorded rows by task. The CSV has no completion-status field, so
        # row presence must not be converted into a success rate.
        tasks = {}
        for row in cw_data:
            tid = row["TaskID"]
            tname = row["TaskName"]
            time_s = row["TimeSeconds"]
            errors = row["Errors"]
            difficulty = row["Difficulty"]
            
            if tid not in tasks:
                tasks[tid] = {"name": tname, "times": [], "errors": [], "difficulties": []}
            
            tasks[tid]["times"].append(time_s)
            tasks[tid]["errors"].append(errors)
            tasks[tid]["difficulties"].append(difficulty)
            
        print(f"{'Task':<16} | {'Rows':<8} | {'Mean Active (s)':<15} | {'SD (s)':<8} | {'Mean Diff. (1-5)':<16}")
        print("-" * 72)
        all_times = []
        for tid in sorted(tasks.keys()):
            t = tasks[tid]
            mean_t, sd_t = calc_mean_sd(t["times"])
            mean_d, _ = calc_mean_sd(t["difficulties"])
            print(f"{tid + ': ' + t['name']:<16} | {len(t['times']):>6}   | {mean_t:>13.2f}   | {sd_t:>6.2f} | {mean_d:>14.2f}")
            all_times.extend(t["times"])
            
        overall_mean_time = sum(all_times) / len(all_times)
        print(f"\nOverall Mean Recorded Active-Interaction Time: {overall_mean_time:.2f} seconds (Paper reports: 9.69)")
        print("Completion status: not reconstructible from this CSV (no row-level completion field).")
        print("The workbook summary reports 80/80 completions; the manuscript discloses but excludes that outcome.\n")
    else:
        print("No walkthrough data found.\n")

    # 3. ACCESSIBILITY QUESTIONNAIRE ANALYSIS
    print("--- 3. ACCESSIBILITY QUESTIONNAIRE ANALYSIS ---")
    aq_data = load_csv(aq_path)
    if aq_data:
        eval_means = {}
        all_ratings = []
        for row in aq_data:
            eid = row["EvaluatorID"]
            rating = row["Rating"]
            if eid not in eval_means:
                eval_means[eid] = []
            eval_means[eid].append(rating)
            all_ratings.append(rating)
            
        eval_scores = [sum(ratings)/len(ratings) for ratings in eval_means.values()]
        mean_aq, sd_aq = calc_mean_sd(eval_scores)
        
        # Rounding analysis (Excel computed mean of the pre-rounded scores: 4.5, 4.5, 4.4, 4.5, 4.9, 4.5, 4.2, 4.9, 4.0, 3.8)
        excel_rounded_means = [4.5, 4.5, 4.4, 4.5, 4.9, 4.5, 4.2, 4.9, 4.0, 3.8]
        mean_excel, sd_excel = calc_mean_sd(excel_rounded_means)
        
        print(f"Overall Mean Questionnaire Rating (True Raw): {mean_aq:.2f}/5")
        print(f"Overall Mean Questionnaire Rating (Excel):    {mean_excel:.2f}/5 (legacy Excel-rounded; paper reports 4.44 True Raw)")
        print(f"Standard Deviation (True Raw):               {sd_aq:.2f}")
        print(f"Standard Deviation (Excel):                  {sd_excel:.2f} (legacy Excel-rounded; paper reports 0.36 True Raw)")
        print(f"Minimum Evaluator Rating:                     {min(eval_scores):.2f}/5")
        print(f"Maximum Evaluator Rating:                     {max(eval_scores):.2f}/5\n")
    else:
        print("No accessibility questionnaire data found.\n")

    # 4. HEURISTIC RATING PROVENANCE
    print("--- 4. HEURISTIC RATING PROVENANCE ---")
    he_data = load_csv(he_path)
    if he_data:
        orig_severities = [row["OriginalSeverity"] for row in he_data]
        rerated_severities = [row["ReRatedSeverity"] for row in he_data]
        
        orig_mean, orig_sd = calc_mean_sd(orig_severities)
        rerated_mean, rerated_sd = calc_mean_sd(rerated_severities)
        
        print("Heuristic Rating Fields (0-4 scale; excluded from principal results):")
        print("Original Coarse Source Field (0/1):")
        print(f"  - Mean rating: {orig_mean:.2f}")
        print(f"  - Std Deviation: {orig_sd:.4f}")
        print("Undocumented Post-Hoc Re-Rating Field:")
        print(f"  - Mean rating: {rerated_mean:.2f}")
        print(f"  - Std Deviation: {rerated_sd:.4f}")
        print("\nExplanation:")
        print("  The coarse source field and the later re-rating field are reproduced only for provenance.")
        print("  The source package does not establish independent item-level observations or a documented")
        print("  re-rating protocol. Neither field supports a severity inference, and both are excluded from")
        print("  the manuscript's principal results.")
    else:
        print("No heuristic rating data found.\n")

if __name__ == "__main__":
    main()
