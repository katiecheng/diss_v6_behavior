import sys
import json
import pandas as pd
import Levenshtein as lev
import numpy as np

### For v5 version deployed 2020-03-10, with n=48 and new behavioral measure

### Get user input for which files to process
if(len(sys.argv) - 1 == 2):
  datePrefix = sys.argv[1]
  versionSampleSuffix = sys.argv[2]
else:
  print("This script takes two arguments, the date prefix and the version/sample suffix for the Firebase json and Prolific csv files.")


### READ ##########################################################################################
### Read Prolific data (toggle if no corresponding Prolific file)
df_prolific = pd.read_csv(
  '../data/raw/{datePrefix}_prolific_export_{versionSampleSuffix}.csv'.format(
    datePrefix=datePrefix,
    versionSampleSuffix=versionSampleSuffix)
)

# df_prolific = pd.read_csv(
#   '../data/raw/{datePrefix}_prolific_export_{versionSampleSuffix}.csv'.format(
#     datePrefix='2020-05-02',
#     versionSampleSuffix='v6n288')
# )

### Read Firebase data
with open(
  '../data/raw/{datePrefix}_diss-v6-behavior-export_{versionSampleSuffix}.json'.format(
    datePrefix=datePrefix,
    versionSampleSuffix=versionSampleSuffix)) as f:
  data=json.load(f)

with open(
'../data/raw/{datePrefix}_diss-v6-behavior-export_{versionSampleSuffix}.json'.format(
  datePrefix='2020-05-02',
  versionSampleSuffix='v6n288')) as f:
    data=json.load(f)

users_dict = data['users']
items_dict = data['items']

df_users = pd.DataFrame.from_dict(users_dict, orient='index')
df_items = pd.DataFrame.from_dict(items_dict, orient='index')


### Read belief change variables
df_belief_change_vars = pd.read_csv(
  'variable_calcs_toImport.csv'
)

### Read behavior change variables
df_behavior_change_vars = pd.read_csv(
  'variable_calcs_behav_toImport.csv'
)

### Read first item behavior variables
# df_behavior_firstItem_vars = pd.read_csv(
#   'variable_calcs_behav_firstItem_toImport.csv'
# )

### Read by item behavior variables
df_behavior_byItem_vars = pd.read_csv(
  'variable_calcs_behav_byItem_toImport.csv'
)

### WRANGLE #######################################################################################
### Drop items with NaN in itemIndex
df_items = df_items.dropna(subset=['itemIndex'])

### reindex dfs
df_prolific = df_prolific.set_index(['participant_id'])
df_prolific.index.names = ['prolificId']
df_users = df_users.set_index(['prolificId'])
df_items = df_items.set_index(['prolificId', 'itemIndex'])


### change types of columns that need calculation

df_users['interventionPredictRestudy'] = pd.to_numeric(df_users['interventionPredictRestudy'], errors='coerce')
df_users['interventionPredictGenerate'] = pd.to_numeric(df_users['interventionPredictGenerate'], errors='coerce')
df_users['interventionTestRestudyScore'] = pd.to_numeric(df_users['interventionTestRestudyScore'], errors='coerce')
df_users['interventionTestGenerateScore'] = pd.to_numeric(df_users['interventionTestGenerateScore'], errors='coerce')

### Do all of the preproc in python

### CREATE VARS TO DETERMINE EXCLUSION CRITERIA ###################################################
### Calculate exclusion criteria
"""
[1-9] restudy strategy
[4] generate strategy
[1-9] restudy test
generate test
[4] intervention test
[4] assessment test

[x] for each item, calculate Levenshtein distance from the correct answer
[x] for each item, create a boolean variable for different Levenshtein cutoff thresholds (1,2,3,4)
[x] for each user, calculate scores (0-10) using different Levenshtein cutoff thresholds
[x] in r, plot each criteria against testScore, look for a step fn between 9 and 10 that is inclusive
"""
### Calculate lev distances

### Calculate interventionStrategyLevDistance
df_items['interventionStrategyLevDistance'] = df_items.apply(lambda row: lev.distance(
  row['itemEnglish'], 
  row['interventionStrategyUserInputRound1']), axis=1)

for n in range(1,3):
  colname = "interventionStrategyLevDist" + str(n)
  df_items[colname] = df_items.apply(lambda row: 
      1 if row['interventionStrategyLevDistance']<=n else 0, axis=1
  )

### Calculate interventionTestLevDistance
df_items['interventionTestLevDistance'] = df_items.apply(lambda row: lev.distance(
  row['itemEnglish'], 
  row['interventionTestUserInput']), axis=1)

for n in range(1,3):
  colname = "interventionTestLevDist" + str(n)
  df_items[colname] = df_items.apply(lambda row: 
      1 if row['interventionTestLevDistance']<=n else 0, axis=1
  )

### Calculate assessmentTestLevDistance
df_items['assessmentTestLevDistance'] = df_items.apply(lambda row: lev.distance(
  row['itemEnglish'], 
  row['assessmentTestUserInput']), axis=1)

for n in range(1,3):
  colname = "assessmentTestLevDist" + str(n)
  df_items[colname] = df_items.apply(lambda row: 
      1 if row['assessmentTestLevDistance']<=n else 0, axis=1
  )

### Groupby to calculate scores
group_pid = df_items.groupby(["prolificId"])
group_pid_restudy = df_items[df_items['interventionStrategy']=="restudy"].groupby(["prolificId"])
group_pid_generate = df_items[df_items['interventionStrategy']=="generate"].groupby(["prolificId"])

### Calculate scores

### Calculate interventionStrategyRestudy score; sum the columns levDist 1-10
for n in range(1,3):
  colname_score = "interventionStrategyRestudyScoreLevDist" + str(n)
  colname_levDist = "interventionStrategyLevDist" + str(n)
  restudyScoreLevDist = pd.DataFrame(group_pid_restudy[colname_levDist].sum()).rename(columns={colname_levDist: colname_score})
  df_users = pd.merge(df_users, restudyScoreLevDist, how='left', on='prolificId')

### Calculate interventionStrategyGenerate score
for n in range(1,3):
  colname_score = "interventionStrategyGenerateScoreLevDist" + str(n)
  colname_levDist = "interventionStrategyLevDist" + str(n)
  generateScoreLevDist = pd.DataFrame(group_pid_generate[colname_levDist].sum()).rename(columns={colname_levDist: colname_score})
  df_users = pd.merge(df_users, generateScoreLevDist, how='left', on='prolificId')

### Calculate interventionTest restudy score
for n in range(1,3):
  colname_score = "interventionTestRestudyScoreLevDist" + str(n)
  colname_levDist = "interventionTestLevDist" + str(n)
  testRestudyScoreLevDist = pd.DataFrame(group_pid_restudy[colname_levDist].sum()).rename(columns={colname_levDist: colname_score})
  df_users = pd.merge(df_users, testRestudyScoreLevDist, how='left', on='prolificId')

### Calculate interventionTest generate score
for n in range(1,3):
  colname_score = "interventionTestGenerateScoreLevDist" + str(n)
  colname_levDist = "interventionTestLevDist" + str(n)
  testGenerateScoreLevDist = pd.DataFrame(group_pid_generate[colname_levDist].sum()).rename(columns={colname_levDist: colname_score})
  df_users = pd.merge(df_users, testGenerateScoreLevDist, how='left', on='prolificId')

### Calculate interventionTest 
for n in range(1,3):
  colname_score = "interventionTestScoreLevDist" + str(n)
  colname_levDist = "interventionTestLevDist" + str(n)
  interventionTestScoreLevDist = pd.DataFrame(group_pid[colname_levDist].sum()).rename(columns={colname_levDist: colname_score})
  df_users = pd.merge(df_users, interventionTestScoreLevDist, how='left', on='prolificId')

### Calculate assessmentTest
for n in range(1,3):
  colname_score = "assessmentTestScoreLevDist" + str(n)
  colname_levDist = "assessmentTestLevDist" + str(n)
  assessmentTestScoreLevDist = pd.DataFrame(group_pid[colname_levDist].sum()).rename(columns={colname_levDist: colname_score})
  df_users = pd.merge(df_users, assessmentTestScoreLevDist, how='left', on='prolificId')

### CREATE ITEM-LEVEL VARS FOR ANALYSES ###########################################################
### Calculate new item-level variables TODO


### CREATE USER-LEVEL VARS FROM ITEM-LEVEL ###########################################################

# create a T/F vector
is_firstItem = df_items['assessmentStrategyOrder']==1
# subset to rows that are T
df_firstItemStrategy = df_items[is_firstItem]
# remove itemIndex as index
df_firstItemStrategy = df_firstItemStrategy.reset_index(level=[1])[['assessmentStrategy']]
# rename strat
df_firstItemStrategy = df_firstItemStrategy.rename(columns={"assessmentStrategy": "firstItemStrategy"})
# merge into users df
df_users = pd.merge(df_users, df_firstItemStrategy, how='left', on='prolificId')

### Repeat this for all 20 assessment items, to get strategy for each
### need this info to calculate consistency
for n in range(1, 21):
  is_nth_item = df_items['assessmentStrategyOrder']==n
  df_nth_item_strategy = df_items[is_nth_item]
  df_nth_item_strategy = df_nth_item_strategy.reset_index(level=[1])[['assessmentStrategy']]
  df_nth_item_strategy = df_nth_item_strategy.rename(columns={"assessmentStrategy": "itemStrategy_%d" %(n)})
  df_users = pd.merge(df_users, df_nth_item_strategy, how='left', on='prolificId')


### CREATE USER-LEVEL VARS FOR ANALYSES ###########################################################
# numeric, difference from expecations: difference actual-predict for restudy and generate separately
# numeric, difference between strategies: difference restudy-generate
# categorical, predict-restudy/generate/equal, actual-restudy/generate/equal, preferred-actual strategy match-yes/no

### interventionTestScore
df_users['interventionTestScore'] = df_users['interventionTestRestudyScore'] + df_users['interventionTestGenerateScore']

### Calculate categories

# Prediction
df_users['diff_interventionPredictRG'] = df_users['interventionPredictRestudy'] - df_users['interventionPredictGenerate']
df_users['interventionPrediction'] = df_users.apply(
  lambda row: "restudy" if row['diff_interventionPredictRG'] >0 else (
    "generate" if row['diff_interventionPredictRG'] <0 else (
      "equal" if row['diff_interventionPredictRG'] ==0 else None)), 
  axis=1
)

# Outcome
df_users['diff_interventionTestOutcomeRG'] = df_users['interventionTestRestudyScore'] - df_users['interventionTestGenerateScore']
df_users['interventionOutcome'] = df_users.apply(
  lambda row: "restudy" if row['diff_interventionTestOutcomeRG'] >0 else (
    "generate" if row['diff_interventionTestOutcomeRG'] <0 else (
      "equal" if row['diff_interventionTestOutcomeRG'] ==0 else None)), 
  axis=1
)

# Belief (v3 only)

# Numeric values for effectiveness ratings; Krosnick tables
effectivenessRating = { 
  "extremely" : 1.69,
  "very" : 1.46,
  "moderately" : .66,
  "slightly" : .44,
  "not" : 0,
  "" : None
}

df_users['effectivenessRestudy_num'] = [effectivenessRating[rating] for rating in df_users['effectivenessRestudy'] ] 
df_users['effectivenessGenerate_num'] = [effectivenessRating[rating] for rating in df_users['effectivenessGenerate'] ] 
df_users['effectivenessGenerate_withHint_num'] = [effectivenessRating[rating] for rating in df_users['effectivenessGenerate_withHint'] ] 

# df_users['effectivenessRestudy_num'] = pd.to_numeric(df_users['effectivenessRestudy_num'], errors='coerce')
# df_users['effectivenessGenerate_num'] = pd.to_numeric(df_users['effectivenessGenerate_num'], errors='coerce')

#effort rating; Carey 2010 Verbal label tables
effortRating = {
  "greatdeal": 77,
  "alot": 55,
  "moderate": 43,
  "alittle": 12,
  "none": 0,
  "" : None
}

df_users['effortRestudy_num'] = [effortRating[rating] for rating in df_users['effortRestudy'] ] 
df_users['effortGenerate_num'] = [effortRating[rating] for rating in df_users['effortGenerate'] ] 
df_users['effortGenerate_withHint_num'] = [effortRating[rating] for rating in df_users['effortGenerate_withHint'] ] 
df_users['effort_num'] = [effortRating[rating] for rating in df_users['effort'] ] 


df_users['diff_assessmentBeliefRG_num'] = df_users['effectivenessRestudy_num'] - df_users['effectivenessGenerate_num']
df_users['assessmentBelief'] = df_users.apply(
  lambda row: "restudy" if row['diff_assessmentBeliefRG_num'] >0 else (
    "generate" if row['diff_assessmentBeliefRG_num'] <0 else (
      "equal" if row['diff_assessmentBeliefRG_num'] ==0 else None)), 
  axis=1
)

df_users['diff_assessmentBehaviorRG_num'] = df_users['assessmentStrategyChoiceRestudyCount'] - df_users['assessmentStrategyChoiceGenerateCount']
df_users['assessmentBehaviorREG'] = df_users.apply(
  lambda row: "restudy" if row['diff_assessmentBehaviorRG_num'] >0 else (
    "generate" if row['diff_assessmentBehaviorRG_num'] <0 else (
      "equal" if row['diff_assessmentBehaviorRG_num'] ==0 else None)), 
  axis=1
)

### Calculate shift in beliefs

# use manually calculated beliefs
# reset_index() and set_index() lets you keep the index after merge
df_users = df_users.reset_index().merge(df_belief_change_vars, how="left").set_index('prolificId')

# use manually calculated behaviors
df_users = df_users.reset_index().merge(df_behavior_change_vars, how="left").set_index('prolificId')

# use manually calculated behaviors firstItem
# df_users = df_users.reset_index().merge(df_behavior_firstItem_vars, how="left").set_index('prolificId')


### Repeat this for all 20 assessment items, to get strategy for each
### need this info to calculate consistency
for n in range(1, 21):
  df_behavior_byItem_vars = df_behavior_byItem_vars.rename(columns={
    "itemStrategy_%d" %(n-1): "itemStrategy_%d" %(n),
    "outcomeMatchPredictionBehavior_%d" %(n-1): "outcomeMatchPredictionBehavior_%d" %(n),
    "directionOfChangeBehavior_%d" %(n-1): "directionOfChangeBehavior_%d" %(n),
    "directionOfChangeBehavior_%d_num" %(n-1): "directionOfChangeBehavior_%d_num" %(n),
    "changeRelativeToOutcomeBehavior_%d" %(n-1): "changeRelativeToOutcomeBehavior_%d" %(n),
    "changeRelativeToOutcomeBehavior_%d_num" %(n-1): "changeRelativeToOutcomeBehavior_%d_num" %(n),
    "behaviorAlignedWithOutcome_%d" %(n-1): "behaviorAlignedWithOutcome_%d" %(n),
    "behaviorAlignedWithOutcome_%d_num" %(n-1): "behaviorAlignedWithOutcome_%d_num" %(n)
    })
  df_users = df_users.reset_index().merge(df_behavior_byItem_vars, how="left").set_index('prolificId')


"""
# Feedback consistent or inconsistent with expectations?
df_users['outcomeMatchPrediction'] = df_users.apply(
  lambda row: None if row['interventionPrediction'] == None else (
    'match' if row['interventionPrediction'] == row['interventionOutcome'] else 'mismatch'), axis=1
)

# Change toward, no change, or away from feedback, given expectations?
df_users['directionOfChange'] = df_users.apply(
  lambda row: None if row['interventionPrediction'] == None or row['assessmentBelief'] == None else (
    'noChange' if row['interventionPrediction'] == row['assessmentBelief'] else (
      'away' if row['interventionPrediction'] == row['interventionOutcome'] else 'toward')), axis=1
)

# Change consistent or inconsistent with expectations, given prediction and outcome
df_users['changeRelativeToOutcome'] = df_users.apply(
  lambda row: 'consistent' if row['outcomeMatchPrediction'] == 'match' and row['directionOfChange'] == 'noChange' else (
    'consistent' if row['directionOfChange'] == 'toward' else (
      'inconsistent' if row['outcomeMatchPrediction'] == 'mismatch' and row['directionOfChange'] == 'noChange' else (
        'inconsistent' if row['directionOfChange'] == 'away' else None))), axis=1
)

df_users['changeRelativeToOutcome_num'] = df_users.apply(
  lambda row: 1 if row['changeRelativeToOutcome'] == 'consistent' else 0, axis=1
)

# Change toward/away/noChange numerical
# Calculates the amount of change from prediction to outcome (0, 1, or 2), and the direction with respect to feedback (toward +, away -)

# test function to make sure it's categorizing correctly; check manually
# test = pd.DataFrame({
#   'interventionPrediction' : ['restudy']*9 + ['equal']*9 + ['generate']*9,
#   'interventionOutcome' : (['restudy']*3 + ['equal']*3 + ['generate']*3) * 3,
#   'assessmentBelief' : ['restudy', 'equal', 'generate']*9
# })


# test['directionOfChange_num'] = test.apply(
#   lambda row: None if row['interventionPrediction'] == None or row['assessmentBelief'] == None else (
#     0 if row['interventionPrediction'] == row['assessmentBelief'] else (
#       -2 if row['interventionPrediction'] == row['interventionOutcome'] and row['interventionPrediction'] != 'equal' and row['assessmentBelief'] != 'equal' else (
#         -1 if row['interventionPrediction'] == row['interventionOutcome'] else (
#           -1 if row['interventionPrediction'] == 'equal' and row['interventionPrediction'] != row['interventionOutcome'] != row['assessmentBelief'] else (
#             2 if row['interventionPrediction'] != 'equal' and row['assessmentBelief'] != 'equal' else 1))))), axis=1
# )

df_users['directionOfChange_num'] = df_users.apply(
  lambda row: None if row['interventionPrediction'] == None or row['assessmentBelief'] == None else (
    0 if row['interventionPrediction'] == row['assessmentBelief'] else (
      -2 if row['interventionPrediction'] == row['interventionOutcome'] and row['interventionPrediction'] != 'equal' and row['assessmentBelief'] != 'equal' else (
        -1 if row['interventionPrediction'] == row['interventionOutcome'] else (
          -1 if row['interventionPrediction'] == 'equal' and row['interventionPrediction'] != row['interventionOutcome'] != row['assessmentBelief'] else (
            2 if row['interventionPrediction'] != 'equal' and row['assessmentBelief'] != 'equal' else 1))))), axis=1
)
"""

### Calculate dimensions of feedback

df_users['diff_interventionRestudyScoreToPrediction'] = df_users['interventionTestRestudyScore'] - df_users['interventionPredictRestudy']
df_users['diff_interventionGenerateScoreToPrediction'] = df_users['interventionTestGenerateScore'] - df_users['interventionPredictGenerate']


### item outcome names
itemConsistencyNames = []
itemAlignmentNames = []
for n in range(1, 21):
  itemConsistencyNames.append("changeRelativeToOutcomeBehavior_%d_num" %n)
  itemAlignmentNames.append("behaviorAlignedWithOutcome_%d_num" %n)


"""
Calculate the number of switches
"""

# vertical in items; make it horizontal in users, for each user, one column for each item strategy
# replace empty string with np.nan so that it will be recognized by notnull()
notNullBooleanSeries = df_items.assessmentStrategyOrder.replace("",np.nan,inplace=False).notnull()
# subset to these three columns (may not be necessary)
# df_items_assessmentStrategies = df_items[notNullBooleanSeries].reset_index()[['prolificId','assessmentStrategyOrder','assessmentStrategy']]
df_items_assessmentStrategies = df_items[notNullBooleanSeries].reset_index()
# create a pivot table, with prolificId as index, assessStratOrder as columns, and assessStrat as values
df_stratsToColumns = df_items_assessmentStrategies.pivot(index='prolificId', columns='assessmentStrategyOrder', values='assessmentStrategy')
df_stratsToColumns = df_stratsToColumns.replace('restudy', 'R').replace('generate', 'G')

# create a string of strategy choices
df_stratsToColumns['assessmentStrategySequence'] = df_stratsToColumns.apply(
    lambda x: ''.join(x.dropna()), # join can join dfs with different indices
    axis=1 # apply to each row
)

# process each string and create a new var: every switch from R->G or G->R is a switch
df_stratsToColumns['assessmentStrategySwitches'] = df_stratsToColumns['assessmentStrategySequence'].apply(
    lambda x: x.count('RG') + x.count('GR')
)

# merge to merge on indices! Wow it worked
df_users = df_users.merge(df_stratsToColumns, left_on="prolificId", right_on="prolificId")

# check
# print(df_users[['assessmentStrategySequence','assessmentStrategySwitches']])


"""
Create a string of strategy accuracies
"""
# vertical in items; make it horizontal in users, for each user, one column for each item accuracy
df_accuraciesToColumns = df_items_assessmentStrategies.pivot(index='prolificId', columns='assessmentStrategyOrder', values='assessmentStrategyAccuracy')
# create a string of strategy choices
df_accuraciesToColumns['assessmentAccuracySequence'] = df_accuraciesToColumns.apply(
    lambda x: ''.join(x.dropna().astype(int).astype(str)),
    axis=1 # apply to each row
)

df_users = df_users.merge(df_accuraciesToColumns, left_on="prolificId", right_on="prolificId")

# check
# print(df_users[['assessmentAccuracySequence']])


"""
Probability next is an R given G-fail vs. G-success

make sequence into a list of lists
[['G', 1], ['G', 0], ...]

iterate through list
maintain counts:
# G0s
# followed by R
# followed by G
# no choice to follow
for each ['G', 0], if index is 19, no choice to follow, else if followed by R +=R, else +=G
"""
# two strings, split them into lists of characters, zip them into a list of lists
df_users['assessmentStratAcc'] = df_users[['assessmentStrategySequence','assessmentAccuracySequence']].apply(
    lambda x: np.array(zip(
            list(str(x['assessmentStrategySequence'])), 
            list(str(x['assessmentAccuracySequence']))
            )) if pd.notnull(x['assessmentStrategySequence']) else x['assessmentStrategySequence'],
    axis=1 # apply to each row
)
# check
# print(df_users['assessmentStratAcc'])

def helperFunc(stratAccList, strategy, accuracy):
    numStratAcc = 0
    numStratAcc_exclude20 = 0
    numStay = 0
    numSwitch = 0
    for i in range(20):
        if pd.isnull(np.array(stratAccList)).all():
            # had to do isnull instead of notnull, else breaks
            pass 
        elif len(stratAccList) < 20:
            pass
        else:
            if (stratAccList[i] == [strategy, accuracy]).all():
                if i < 19:
                    numStratAcc += 1
                    numStratAcc_exclude20 += 1
                    if stratAccList[i+1][0] == strategy:
                        numStay += 1
                    else:
                        numSwitch += 1
                else:
                    numStratAcc += 1
    if numStratAcc_exclude20 > 0:
        probStay = numStay / float(numStratAcc_exclude20)
        probSwitch = numSwitch / float(numStratAcc_exclude20)
    else:
        probStay = float("nan")
        probSwitch = float("nan")
    return (numStratAcc, probStay, probSwitch)


def calcProbabilityStaySwitch(df, strategy, accuracy):
    df_users['howMany_%s_%s' %(strategy, accuracy)], \
    df_users['probStay_after_%s_%s' %(strategy, accuracy)], \
    df_users['probSwitch_after_%s_%s' %(strategy, accuracy)] = \
    zip(*df_users['assessmentStratAcc'].map(lambda seq: helperFunc(seq, strategy, accuracy)))


calcProbabilityStaySwitch(df_users, "G", "0")
calcProbabilityStaySwitch(df_users, "R", "0")
calcProbabilityStaySwitch(df_users, "G", "1")
calcProbabilityStaySwitch(df_users, "R", "1")


### sort on column names
df_users = df_users[[
  "startDateTime",
  "endDateTime",
  "condition",
  "interventionStrategyRestudyScoreRound1",
  "interventionStrategyRestudyScoreLevDist1",
  "interventionStrategyRestudyScoreLevDist2",
  "interventionStrategyGenerateScoreRound1",
  "interventionStrategyGenerateScoreLevDist1",
  "interventionStrategyGenerateScoreLevDist2",
  "interventionStrategyRestudyScoreRound2",
  "interventionStrategyGenerateScoreRound2",
  "interventionPredictRestudy",
  "interventionPredictRestudyReason",
  "interventionPredictGenerate",
  "interventionPredictGenerateReason",
  "interventionPrediction",
  "diff_interventionPredictRG",
  "interventionTestRestudyScore",
  "interventionTestRestudyScoreLevDist1",
  "interventionTestRestudyScoreLevDist2",
  "interventionTestGenerateScore",
  "interventionTestGenerateScoreLevDist1",
  "interventionTestGenerateScoreLevDist2",
  "interventionTestScore",
  "interventionTestScoreLevDist1",
  "interventionTestScoreLevDist2",
  "interventionOutcome",
  "diff_interventionTestOutcomeRG",
  "diff_interventionRestudyScoreToPrediction",
  "diff_interventionGenerateScoreToPrediction",
  "interventionFeedbackSurprise",
  "assessmentStrategyChoiceRestudyCount",
  "assessmentStrategyChoiceGenerateCount",
  "assessmentStrategyRestudyScore",
  "assessmentStrategyGenerateScore",
  "assessmentStrategySequence",
  "assessmentStrategySwitches",
  # "assessmentAccuracySequence",
  "assessmentStratAcc",
  "howMany_G_1",
  "probStay_after_G_1",
  "probSwitch_after_G_1",
  "howMany_G_0",
  "probStay_after_G_0",
  "probSwitch_after_G_0",
  "howMany_R_1",
  "probStay_after_R_1",
  "probSwitch_after_R_1",
  "howMany_R_0",
  "probStay_after_R_0",
  "probSwitch_after_R_0",
  "assessmentTestScore",
  "assessmentTestRestudyScore",
  "assessmentTestGenerateScore",
  "assessmentTestScoreLevDist1",
  "assessmentTestScoreLevDist2",
  # "totalScore",
  # "bonusPayment",
  "effectivenessRestudy",
  "effectivenessRestudy_num",
  "effortRestudy",
  "effortRestudy_num",
  # "howManyRestudy",
  "effectivenessGenerate",
  "effectivenessGenerate_num",
  "effortGenerate",
  "effortGenerate_num",
  # "howManyGenerate",
  "effectivenessGenerate_withHint",
  "effectivenessGenerate_withHint_num",
  "effortGenerate_withHint",
  "effortGenerate_withHint_num",
  "chosenStrategy",
  "assessmentBelief",
  "diff_assessmentBeliefRG_num",
  "outcomeMatchPrediction",
  "directionOfChange",
  "directionOfChange_num",
  "changeRelativeToOutcome",
  "changeRelativeToOutcome_num",
  "assessmentBehaviorREG",
  "outcomeMatchPredictionBehavior",
  "directionOfChangeBehavior",
  "directionOfChangeBehavior_num",
  "changeRelativeToOutcomeBehavior",
  "changeRelativeToOutcomeBehavior_num",
  "itemStrategy_1",
  "outcomeMatchPredictionBehavior_1",
  "directionOfChangeBehavior_1",
  "directionOfChangeBehavior_1_num",
  "changeRelativeToOutcomeBehavior_1",
  "effort",
  "effort_num",
  "comments"
] + itemConsistencyNames + itemAlignmentNames]

df_items = df_items[[
  "itemSwahili",
  "itemEnglish",
  "interventionStudyOrder",
  "interventionStrategyOrder",
  "interventionTestOrder",
  "interventionStrategy",
  "interventionStrategyUserInputRound1",
  "interventionStrategyAccuracyRound1",
  "interventionStrategyLevDistance",
  "interventionStrategyLevDist1",
  "interventionStrategyLevDist2",
  "interventionStrategyUserInputRound2",
  "interventionStrategyAccuracyRound2",
  "interventionTestUserInput",
  "interventionTestAccuracy",
  "interventionTestLevDist1",
  "interventionTestLevDist2",
  "assessmentStudyOrder",
  "assessmentStrategyOrder",
  "assessmentTestOrder",
  "assessmentStrategy",
  "assessmentStrategyUserInput",
  "assessmentStrategyAccuracy",
  "assessmentTestUserInput",
  "assessmentTestAccuracy",
  "assessmentTestLevDist1",
  "assessmentTestLevDist2"
]]


### Link item-level data to user-level data, for a user-level analysis file
### sorted on column names, reverse alpha 
### join on index, keeping hierarchy
# print("users index: ", df_users.index)
# print("items index: ", df_items.index)
df_users_items = df_users.join(df_items, how='inner')


### sort on column values 
#(for expt v2 and beyond)
df_users_items = df_users_items.sort_values([
  'prolificId',
  'assessmentStrategy',
  'interventionStrategy',
  'interventionStrategyOrder',
  'assessmentStrategyOrder'
])

### Add prolific data! 
#(removes the rows that don't have corresponding ids in the prolific file)
df_users_items = df_prolific.join(df_users_items, how='inner')
df_users = df_prolific.join(df_users, how='inner')

### Create df for bonuses
# df_bonus = df_users_items[[
#   'prolificId',
#   'bonusPayment'
# ]]

### Output to csv for R
df_users_items.to_csv(
  "../data/{datePrefix}_diss-v6-behavior_df-users-items_{versionSampleSuffix}.csv".format(
    datePrefix=datePrefix,
    versionSampleSuffix=versionSampleSuffix
  ), encoding='utf-8'
)

### Output to csv for R, users df only
df_users.to_csv(
  "../data/{datePrefix}_diss-v6-behavior_df-users-items_{versionSampleSuffix}_users.csv".format(
    datePrefix=datePrefix,
    versionSampleSuffix=versionSampleSuffix
  ), encoding='utf-8'
)

### Output to csv for bonus payment
# df_bonus.to_csv(
#   "../data/{datePrefix}_diss-pilot-expt1_df-users-items_{versionSampleSuffix}_bonusPayment.csv".format(
#   datePrefix=datePrefix,
#   versionSampleSuffix=versionSampleSuffix
#   ), encoding='utf-8'
# )
