dir_proj <- here::here(); dir_proj
dir_data <- fs::path(dir_proj, "data"); dir_data

df_v6n288 = read_csv(fs::path(dir_data, "2020-05-02_diss-v6-behavior_df-users-items_v6n288.csv"), col_names=TRUE)
df_v6n288_users = read_csv(fs::path(dir_data, "2020-05-02_diss-v6-behavior_df-users-items_v6n288_users.csv"), col_names=TRUE)

# keep only approved
df_v6n288_users <- filter(df_v6n288_users, status=="APPROVED" & !is.na(effort)); nrow(df_v6n288_users)

# Create new dfs  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

#TODO fix so no error; upon import, treating all text areas as factors instead of character vectors

v5FactCols_users <- c("prolificId",
                      #"overallBetterWorseSame",
                      #"noticedStrategy",
                      "effectivenessRestudy", 
                      "effortRestudy",
                      "effectivenessGenerate", 
                      "effortGenerate",
                      "chosenStrategy", 
                      "effort", 
                      "assessmentBelief", 
                      "directionOfChange", 
                      "changeRelativeToOutcome")

v5FactCols_items <- c("prolificId",
                      "effectivenessRestudy", 
                      "effortRestudy",
                      "effectivenessGenerate", 
                      "effortGenerate",
                      "chosenStrategy", 
                      "effort", 
                      "assessmentBelief", 
                      "directionOfChange", 
                      "changeRelativeToOutcome")

v5NumCols <- c("age",
               "reviewed_at_datetime",
               "effectivenessRestudy_num", 
               "effortRestudy_num",
               "effectivenessGenerate_num", 
               "effortGenerate_num",
               "diff_assessmentBeliefRG_num", 
               "effort_num",
               "directionOfChange_num", 
               "changeRelativeToOutcome_num")

df_v6n288_users[v5FactCols_users] <- lapply(df_v6n288_users[v5FactCols_users], factor)
df_v6n288_users[v5NumCols] <- lapply(df_v6n288_users[v5NumCols], as.numeric)
df_v6n288[v5FactCols_items] <- lapply(df_v6n288[v5FactCols_items], factor)
df_v6n288[v5NumCols] <- lapply(df_v6n288[v5NumCols], as.numeric)

# drop excluded  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# calculate summary stats across group for exclusion

m_restudyScore_v6n288 <- mean(df_v6n288_users$interventionStrategyRestudyScoreRound1, na.rm=T); m_restudyScore_v6n288 # 8.9
s_restudyScore_v6n288 <- sd(df_v6n288_users$interventionStrategyRestudyScoreRound1, na.rm=T); s_restudyScore_v6n288 # 1.99

# drop at user level (restudyScore 3 SD below mean)
df_v6n288_users <- filter(df_v6n288_users, interventionStrategyRestudyScoreRound1 >= m_restudyScore_v6n288 - 3*s_restudyScore_v6n288); nrow(df_v6n288_users) # 47

# drop at item level
df_v6n288 <- filter(df_v6n288, prolificId %in% df_v6n288_users$prolificId); nrow(df_v6n288)/40
