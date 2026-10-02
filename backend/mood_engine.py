WORDS={'angry':['angry','furious','mad','irritated','annoyed'],'sad':['sad','cry','crying','heartbroken','upset'],'stressed':['stress','stressed','pressure','overwhelmed','exam','deadline'],'confused':['confused','lost','unsure','uncertain'], 'lonely':['lonely','alone','isolated'],'bored':['bored','boring','nothing to do'],'tired':['tired','exhausted','sleepy','drained'],'anxious':['anxious','anxiety','worried','worry','panic','nervous'],'happy':['happy','good','great','excited','joy']}
DANGER=['suicide','suicidal','kill myself','hurt myself','self harm','end my life','want to die']
def detect_mood(t):
 t=t.lower(); scores={m:sum(k in t for k in ks) for m,ks in WORDS.items()}; m=max(scores,key=scores.get); return (m,'keyword-based demo') if scores[m] else ('neutral','prototype')
def detect_danger(t): return any(x in t.lower() for x in DANGER)
