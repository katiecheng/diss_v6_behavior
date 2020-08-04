
# Update variable types # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

df_v6n288_users$condition <- factor(df_v6n288_users$condition,
                                   levels=c(0,1,2),
                                   labels=c("control", "expt1", "expt2"))

df_v6n288$condition <- factor(df_v6n288$condition,
                             levels=c(0,1,2),
                             labels=c("control", "expt", "expt2"))

# Create new variables # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# feedback type (none, equal, restudy, generate)

df_v6n288_users$feedback <- factor(ifelse(
  df_v6n288_users$condition=="control", "none",
  ifelse(df_v6n288_users$interventionOutcome=="equal", "equal",
         ifelse(df_v6n288_users$interventionOutcome=="restudy", "restudy", "generate"))))

df_v6n288$feedback <- factor(ifelse(
  df_v6n288$condition=="control", "none",
  ifelse(df_v6n288$interventionOutcome=="equal", "equal",
         ifelse(df_v6n288$interventionOutcome=="restudy", "restudy", "generate"))))

df_v6n288$assessmentStrategy_num <- factor(ifelse(
  df_v6n288$assessmentStrategy=="restudy", 0,
  ifelse(df_v6n288$assessmentStrategy=="generate", 1, NA)))

# calculate effort diff
df_v6n288_users$diff_assessmentBeliefEffortRG_num <- df_v6n288_users$effortRestudy_num - df_v6n288_users$effortGenerate_num

# which exceeded expectations more?
df_v6n288_users$diff_interventionStrategyScoreExceedPrediction <- df_v6n288_users$diff_interventionRestudyScoreToPrediction - 
  df_v6n288_users$diff_interventionGenerateScoreToPrediction

# scale predictions to be on the same scale as effectiveness ratings

scaling_constant <- 10/1.69

df_v6n288_users$changeBeliefRG_num <- df_v6n288_users$diff_assessmentBeliefRG_num - (df_v6n288_users$diff_interventionPredictRG * scaling_constant)

df_v6n288_users$diff_assessmentBeliefRG_scale10 <- df_v6n288_users$diff_assessmentBeliefRG_num * scaling_constant

# reorder variable levels

df_v6n288_users$interventionPrediction <- factor(df_v6n288_users$interventionPrediction, levels = c("generate", "equal", "restudy"))
df_v6n288_users$interventionOutcome <- factor(df_v6n288_users$interventionOutcome, levels = c("generate", "equal", "restudy"))
df_v6n288_users$assessmentBelief <- factor(df_v6n288_users$assessmentBelief, levels = c("generate", "equal", "restudy"))
df_v6n288_users$assessmentBehaviorREG <- factor(df_v6n288_users$assessmentBehaviorREG, levels = c("generate", "equal", "restudy"))

# REG to numeric
df_v6n288_users$interventionPrediction_num <- ifelse(df_v6n288_users$interventionPrediction =="generate", -1, 
                                                    ifelse(df_v6n288_users$interventionPrediction == "equal", 0, 
                                                           ifelse(df_v6n288_users$interventionPrediction == "restudy", 1, NA)))
df_v6n288_users$interventionOutcome_num <- ifelse(df_v6n288_users$interventionOutcome =="generate", -1, 
                                                 ifelse(df_v6n288_users$interventionOutcome == "equal", 0, 
                                                        ifelse(df_v6n288_users$interventionOutcome == "restudy", 1, NA)))
df_v6n288_users$assessmentBelief_num <- ifelse(df_v6n288_users$assessmentBelief =="generate", -1, 
                                              ifelse(df_v6n288_users$assessmentBelief == "equal", 0, 
                                                     ifelse(df_v6n288_users$assessmentBelief == "restudy", 1, NA)))

# change beliefs
df_v6n288_users$changeBeliefs <- df_v6n288_users$interventionPrediction != df_v6n288_users$assessmentBelief

# outcome measures
df_v6n288_users$finalMatchOutcome <- df_v6n288_users$interventionOutcome == df_v6n288_users$assessmentBelief
df_v6n288_users$finalMatchOutcome_num <- ifelse(df_v6n288_users$finalMatchOutcome, 1, 0)

df_v6n288_users$firstItemStrategyMatchOutcome  <- df_v6n288_users$interventionOutcome == df_v6n288_users$itemStrategy_1
df_v6n288_users$firstItemStrategyMatchOutcome_num  <- ifelse(df_v6n288_users$firstItemStrategyMatchOutcome, 1, 0)

df_v6n288_users$finalBehaviorMatchOutcome <- df_v6n288_users$interventionOutcome == df_v6n288_users$assessmentBehaviorREG
df_v6n288_users$finalBehaviorMatchOutcome_num <- ifelse(df_v6n288_users$finalBehaviorMatchOutcome, 1, 0)

# behavior diffRG
df_v6n288_users$diff_assessmentBehaviorRG <- df_v6n288_users$assessmentStrategyChoiceRestudyCount - df_v6n288_users$assessmentStrategyChoiceGenerateCount

# success rate
df_v6n288_users$assessmentStrategyRestudySuccessRate <- df_v6n288_users$assessmentStrategyRestudyScore / df_v6n288_users$assessmentStrategyChoiceRestudyCount
df_v6n288_users$assessmentStrategyGenerateSuccessRate <- df_v6n288_users$assessmentStrategyGenerateScore / df_v6n288_users$assessmentStrategyChoiceGenerateCount

df_v6n288_users$highGenerateSuccessRate <- df_v6n288_users$assessmentStrategyGenerateSuccessRate >= .5
df_v6n288_users$highGenerateSuccessRate_num <- ifelse(df_v6n288_users$assessmentStrategyGenerateSuccessRate, 1, 0)

# effort diffRG
df_v6n288_users$diff_effortRG  <- df_v6n288_users$effortRestudy_num - df_v6n288_users$effortGenerate_num


# diff test 2 to test 1
df_v6n288_users$changeTestScore <- df_v6n288_users$assessmentTestScore - df_v6n288_users$interventionTestScore

# drop unused factor levels
df_v6n288 <- droplevels(df_v6n288)
df_v6n288_users <- droplevels(df_v6n288_users)

# subset dfs
df_v6n288_users_control <- filter(df_v6n288_users, condition=="control"); nrow(df_v6n288_users_control)
df_v6n288_users_expt <- filter(df_v6n288_users, condition=="expt"); nrow(df_v6n288_users_expt)
df_v6n288_users_predRoutG <- filter(df_v6n288_users, interventionPrediction=="restudy" & interventionOutcome=="generate"); nrow(df_v6n288_users_predRoutG)
df_v6n288_users_filterNat <- filter(df_v6n288_users, Nationality=="United States"); nrow(df_v6n288_users_filterNat) # 265

# create dataset for CPA in SPSS
subsetVars <- df_v6n288_users[c("condition", 
                                "interventionPrediction",
                                "diff_interventionPredictRG",
                                "interventionOutcome",
                                "diff_interventionTestOutcomeRG",
                                "assessmentStrategyChoiceGenerateCount",
                                "assessmentStrategyGenerateSuccessCount",
                                "assessmentStrategyGenerateFailureCount",
                                "assessmentTestScore",
                                "assessmentBelief",
                                "diff_assessmentBeliefRG_num"
)]

write.csv(subsetVars,fs::path(dir_data, "2020-05-02_diss-v6-behavior_df-users-items_v6n288_afterWrangle_subsetVars.csv"), row.names = FALSE)
