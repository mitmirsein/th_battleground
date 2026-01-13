#!/usr/bin/env python3
"""
Kerygma Daily - Stage 2: Foundation (Exegetical Work)
Week 4 (Feb 22-28, 2026) - First Week of Lent
"""

import json

# Week 4 Foundation Data with Hebrew/Greek parsing
week4_foundation = {
    "2026-02-22": {
        "date": "2026-02-22",
        "liturgical": "First Sunday in Lent",
        "ot": {
            "ref": "창세기 2:16-17",
            "lang": "hebrew",
            "text_dir": "rtl",
            "lang_class": "hebrew",
            "kor_std": "여호와 하나님이 그 사람에게 명하여 이르시되 동산 각종 나무의 열매는 네가 임의로 먹되 선악을 알게 하는 나무의 열매는 먹지 말라 네가 먹는 날에는 반드시 죽으리라 하시니라",
            "kor_lit": "그리고 명령하셨다(와예차우) 여호와 하나님께서(야훼 엘로힘) 그 사람에게(알-하아담) 말씀하시기를(레모르). 모든 나무로부터(미콜-에츠) 그 동산의(하간) 먹는 것은(아콜) 너는 먹을 것이다(토켈). 그러나 나무는(우메에츠) 지식의(하다아트) 선과 악의(토브 와라) 먹지 말라(로 토칼) 그것으로부터(밈멘누). 왜냐하면 그 날에(키 베욤) 너의 먹음에(아콜레카) 그것으로부터(밈멘누) 죽음으로(모트) 너는 죽을 것이기 때문이다(타무트).",
            "eng_bsb": "And the LORD God commanded the man, 'You may freely eat from every tree of the garden, but you must not eat from the tree of the knowledge of good and evil; for in the day that you eat of it, you will surely die.'",
            "focus_text": "וַיְצַו יְהוָה אֱלֹהִים עַל־הָאָדָם לֵאמֹר מִכֹּל עֵץ־הַגָּן אָכֹל תֹּאכֵל וּמֵעֵץ הַדַּעַת טוֹב וָרָע לֹא תֹאכַל מִמֶּנּוּ כִּי בְּיוֹם אֲכָלְךָ מִמֶּנּוּ מוֹת תָּמוּת",
            "words": [
                {"text": "וַיְצַו", "sound": "와예차우", "lemma": "צָוָה", "lemma_sound": "차와", "morph": "접+동 피엘 미완 3남단", "gloss": "그가 명령하셨다"},
                {"text": "יְהוָה אֱלֹהִים", "sound": "야훼 엘로힘", "lemma": "יְהוָה + אֱלֹהִים", "lemma_sound": "야훼 + 엘로힘", "morph": "고유명+명 남복", "gloss": "여호와 하나님께서"},
                {"text": "עַל־הָאָדָם", "sound": "알-하아담", "lemma": "אָדָם", "lemma_sound": "아담", "morph": "전+관+명", "gloss": "그 사람에게"},
                {"text": "לֵאמֹר", "sound": "레모르", "lemma": "אָ마르", "lemma_sound": "아마르", "morph": "전+동 칼 부정사", "gloss": "말씀하시기를"},
                {"text": "מִכֹּל עֵץ־הַגָּן", "sound": "미콜-에츠-하간", "lemma": "עֵץ + גַּן", "lemma_sound": "에츠 + 간", "morph": "전+명+명 연계+관+명", "gloss": "동산의 모든 나무로부터"},
                {"text": "אָכֹל תֹּאכֵל", "sound": "아콜 토켈", "lemma": "אָכַל", "lemma_sound": "아칼", "morph": "동 칼 부정사 절대+동 칼 미완 2남단", "gloss": "먹는 것은 너는 먹을 것이다"},
                {"text": "וּמֵעֵץ", "sound": "우메에츠", "lemma": "עֵץ", "lemma_sound": "에츠", "morph": "접+전+명 연계", "gloss": "그러나 나무는"},
                {"text": "הַדַּעַת", "sound": "하다아트", "lemma": "דַּעַת", "lemma_sound": "다아트", "morph": "관+명", "gloss": "지식의"},
                {"text": "טוֹב וָרָع", "sound": "토브 와라", "lemma": "טוֹב + רַע", "lemma_sound": "토브 + 라", "morph": "형+접+형", "gloss": "선과 악의"},
                {"text": "לֹא תֹאכַל", "sound": "로 토칼", "lemma": "אָכַל", "lemma_sound": "아칼", "morph": "부정어+동 칼 미완 2남단", "gloss": "먹지 말라"},
                {"text": "מִמֶּנּוּ", "sound": "밈멘누", "lemma": "מִן", "lemma_sound": "민", "morph": "전+접미 3남단", "gloss": "그것으로부터"},
                {"text": "כִּ이", "sound": "키", "lemma": "כִּי", "lemma_sound": "키", "morph": "접속사", "gloss": "왜냐하면"},
                {"text": "בְּיוֹם", "sound": "베욤", "lemma": "יוֹם", "lemma_sound": "욤", "morph": "전+명", "gloss": "그 날에"},
                {"text": "אֲכָלְךָ", "sound": "아콜레카", "lemma": "אָכַל", "lemma_sound": "아칼", "morph": "동 칼 부정사 연계+접미 2남단", "gloss": "너의 먹음에"},
                {"text": "מִמֶּנּוּ", "sound": "밈멘누", "lemma": "מִן", "lemma_sound": "민", "morph": "전+접미 3남단", "gloss": "그것으로부터"},
                {"text": "מוֹת תָּמוּת", "sound": "모트 타무트", "lemma": "מוּת", "lemma_sound": "무트", "morph": "동 칼 부정사 절대+동 칼 미완 2남단", "gloss": "죽음으로 너는 죽을 것이다"}
            ]
        },
        "nt": {
            "ref": "로마서 5:18-19",
            "lang": "greek",
            "text_dir": "ltr",
            "lang_class": "greek",
            "kor_std": "그런즉 한 범죄로 많은 사람이 정죄에 이른 것 같이 한 의로운 행위로 말미암아 많은 사람이 의롭다 하심을 받아 생명에 이르렀느니라 한 사람이 순종하지 아니함으로 많은 사람이 죄인 된 것 같이 한 사람이 순종하심으로 많은 사람이 의인이 되리라",
            "kor_lit": "그러므로(아라 운) 마치(호스) 하나를 통하여(디 헤노스) 범죄의(파랍토마토스) 모든 사람들에게(에이스 판타스 안드로푸스) 정죄로(에이스 카타크리마). 그렇게(후토스) 또한(카이) 하나를 통하여(디 헤노스) 의로운 행위의(디카이오마토스) 모든 사람들에게(에이스 판타스 안드로푸스) 의롭다 하심이(디카이오신) 생명으로(조에스). 왜냐하면(가르) 마치(호스페르) 그 한 사람의(투 헤노스 안드로푸) 불순종을 통하여(디아 테스 파라코에스) 죄인들로(하마르톨로이) 많은 이들이 세워졌듯이(카테스타데산 호이 폴로이). 그렇게(후토스) 또한(카이) 그 한 분의(투 헤노스) 순종을 통하여(디아 테스 휘파코에스) 의인들로(디카이오이) 많은 이들이 세워질 것이기 때문이다(카타스타데손탈 호이 폴로이).",
            "eng_bsb": "So then, just as one trespass brought condemnation for all men, so also one act of righteousness brought justification and life for all men. For just as through the disobedience of the one man the many were made sinners, so also through the obedience of the one man the many will be made righteous.",
            "focus_text": "Ἄρα οὖν ὡς δι' ἑνὸς παραπτώματος εἰς πάντας ἀνθρώπους εἰς κατάκριμα οὕτως καὶ δι' ἑνὸς δικαιώματος εἰς πάντας ἀνθρώπους εἰς δικα이ωσιν ζωῆς ὥ스πεר γὰר διὰ τῆς παρα코ῆς τοῦ ἑνὸς ἀνθρώπου ἁما르톨로이 카테스타데산 호이 폴로이 후토스 카이 디아 테스 휘파코ῆς τοῦ ἑνὸς δίκαι오이 카타스타데손탈 호이 폴로이",
            "words": [
                {"text": "Ἄ라 οὖν", "sound": "아라 운", "lemma": "ἄ라 + οὖν", "lemma_sound": "아라 + 운", "morph": "접속사+접속사", "gloss": "그러므로"},
                {"text": "ὡς", "sound": "호스", "lemma": "ὡς", "lemma_sound": "호스", "morph": "접속사", "gloss": "마치"},
                {"text": "디' ἑνὸς", "sound": "디 헤노스", "lemma": "διά + εἷς", "lemma_sound": "디아 + 헤이스", "morph": "전치사+수사 소유격 남단", "gloss": "하나를 통하여"},
                {"text": "파랍토마토스", "sound": "파랍토마토스", "lemma": "παράπτωμα", "lemma_sound": "파랍토마", "morph": "명 소유격 중단", "gloss": "범죄"},
                {"text": "에이스 판타스 안드로푸스", "sound": "에이스 판타스 안드로푸스", "lemma": "εἰς + πᾶς + ἄνθρωπος", "lemma_sound": "에이스 + 파스 + 안드로포스", "morph": "전+형 대격 남복+명 대격 남복", "gloss": "모든 사람들에게"},
                {"text": "에이스 카타크리마", "sound": "에이스 카타크리마", "lemma": "카타크리마", "lemma_sound": "카타크리마", "morph": "전+명 대격 중단", "gloss": "정죄로"},
                {"text": "후토스 카이", "sound": "후토스 카이", "lemma": "후토 + καί", "lemma_sound": "후토 + 카이", "morph": "부사+접속사", "gloss": "그렇게 또한"},
                {"text": "디' ἑνὸς", "sound": "디 헤노스", "lemma": "διά + εἷς", "lemma_sound": "디아 + 헤이스", "morph": "전치사+수사 소유격 남단", "gloss": "하나를 통하여"},
                {"text": "디카이오마토스", "sound": "디카이오마토스", "lemma": "디카이오마", "lemma_sound": "디카이오마", "morph": "명 소유격 중단", "gloss": "의로운 행위"},
                {"text": "에이스 판타스 안드로푸스", "sound": "에이스 판타스 안드로푸스", "lemma": "εἰς + πᾶς + ἄνθρωπος", "lemma_sound": "에이스 + 파스 + 안드로포스", "morph": "전+형 대격 남복+명 대격 남복", "gloss": "모든 사람들에게"},
                {"text": "에이스 디카이오신", "sound": "에이스 디카이오신", "lemma": "디카이오시스", "lemma_sound": "디카이오시스", "morph": "전+명 대격 여단", "gloss": "의롭다 하심으로"},
                {"text": "조에스", "sound": "조에스", "lemma": "조에", "lemma_sound": "조에", "morph": "명 소유격 여단", "gloss": "생명의"},
                {"text": "호스페르 가르", "sound": "호스페르 가르", "lemma": "호스페르 + γάρ", "lemma_sound": "호스페르 + 가르", "morph": "접속사+접속사", "gloss": "왜냐하면 마치"},
                {"text": "디아 테스 파라코에스", "sound": "디아 테스 파라코에스", "lemma": "διά + 파라코에", "lemma_sound": "디아 + 파라코에", "morph": "전+관+명 소유격 여단", "gloss": "그 불순종을 통하여"},
                {"text": "투 헤노스 안드로푸", "sound": "투 헤노스 안드로푸", "lemma": "εἷς + ἄνθρωπος", "lemma_sound": "헤이스 + 안드로포스", "morph": "관+수사 소유격 남단+명 소유격 남단", "gloss": "그 한 사람의"},
                {"text": "하마르톨로이", "sound": "하마르톨로이", "lemma": "하마르톨로스", "lemma_sound": "하마르톨로스", "morph": "형 주격 남복", "gloss": "죄인들로"},
                {"text": "카테스타데산", "sound": "카테스타데산", "lemma": "카디스테미", "lemma_sound": "카디스테미", "morph": "동 부정과거 수동 직설 3복", "gloss": "세워졌다"},
                {"text": "호이 폴로이", "sound": "호이 폴로이", "lemma": "폴리스", "lemma_sound": "폴리스", "morph": "관+형 주격 남복", "gloss": "많은 이들이"},
                {"text": "후토스 카이", "sound": "후토스 카이", "lemma": "후토 + καί", "lemma_sound": "후토 + 카이", "morph": "부사+접속사", "gloss": "그렇게 또한"},
                {"text": "디아 테스 휘파코에스", "sound": "디아 테스 휘파코에스", "lemma": "διά + 휘파코에", "lemma_sound": "디아 + 휘파코에", "morph": "전+관+명 소유격 여단", "gloss": "그 순종을 통하여"},
                {"text": "투 헤노스", "sound": "투 헤노스", "lemma": "εἷς", "lemma_sound": "헤이스", "morph": "관+수사 소유격 남단", "gloss": "그 한 분의"},
                {"text": "디카이오이", "sound": "디카이오이", "lemma": "디카이오스", "lemma_sound": "디카이오스", "morph": "형 주격 남복", "gloss": "의인들로"},
                {"text": "카카타스타데손탈", "sound": "카타스타데손탈", "lemma": "카디스테미", "lemma_sound": "카디스테미", "morph": "동 미래 수동 직설 3복", "gloss": "세워질 것이다"},
                {"text": "호이 폴로이", "sound": "호이 폴로이", "lemma": "폴리스", "lemma_sound": "폴리스", "morph": "관+형 주격 남복", "gloss": "많은 이들이"}
            ]
        },
        "keywords": ["명령", "불순종", "죽음", "순종", "칭의"]
    },
    
    "2026-02-23": {
        "date": "2026-02-23",
        "liturgical": "Monday of Lent Week 1",
        "ot": {
            "ref": "열왕기상 19:5-7",
            "lang": "hebrew",
            "text_dir": "rtl",
            "lang_class": "hebrew",
            "kor_std": "로뎀 나무 아래에 누워 자더니 천사가 그를 어루만지며 그에게 이르되 일어나 먹으라 하는지라 본즉 머리맡에 숯불에 구운 떡과 한 병 물이 있더라 이에 먹고 마시고 다시 누웠더니 여호와의 천사가 또 다시 와서 어루만지며 이르되 일어나 먹으라 네가 갈 길이 멀니라 하는지라",
            "kor_lit": "그리고 그가 누웠다(와예쉬카브) 그리고 잠들었다(와예샨) 로뎀나무 아래(타하트 로템 에하드). 그리고 보라(웨힌네) 천사가(말아크) 만지고 있다(노게아) 그에게(보) 그리고 그에게 말했다(와요메르 로) 일어나라(쿰) 먹으라(에콜). 그리고 그가 봤다(와야베트) 그리고 보라(웨힌네) 그의 머리맡에(메라쇼타이우) 구운 떡(우갓-레차핌) 바위들 위의(레차베) 그리고 병의(웨차파하트) 물(마임). 그리고 그가 먹었다(와요칼) 그리고 그가 마셨다(와예쉬트) 그리고 그가 돌아와 누웠다(와야솨브 와예쉬카브). 그리고 여호와의 천사가 돌아왔다(와야솨브 말아크 야훼) 두 번째로(쉐니트) 그리고 만졌다(와예가) 그에게(보) 그리고 말했다(와요메르) 일어나라(쿰) 먹으라(에콜) 왜냐하면(키) 너무 많다(라브) 너로부터(밈카) 그 길이(하데레크).",
            "eng_bsb": "Then he lay down under the broom tree and fell asleep. Suddenly an angel touched him and said, 'Get up and eat.' And he looked around, and there by his head was a cake of bread baked over hot coals, and a jar of water. So he ate and drank and lay down again. A second time the angel of the LORD returned and touched him, saying, 'Get up and eat, or the journey will be too much for you.'",
            "focus_text": "וַיִּשְׁכַּב וַיִּישָׁן תַּחַת רֹתֶם אֶחָד וְהִנֵּה־מַลְאָךְ נֹגֵעַ בּוֹ וַיֹּאמֶר לוֹ קוּם אֱכוֹל וַיַּבֵּט וְהִנֵּה מְרַ아ֲשֹׁתָיו עֻגַת־רְצָפִים וְצַפַּחַת מָיִם וַיֹּאכַל וַיֵּשְׁתְּ וַיָּשָׁב וַיִּשְׁכָּב וַיָּשָׁב מַלְאַךְ יְהוָה שֵׁנִית וַיִּגַּע בּוֹ וַיֹּאמֶר קוּם אֱכוֹל כִּי רַב מִמְּךָ הַדָּרֶךְ",
            "words": [
                {"text": "וַיִּשְׁכַּב", "sound": "와예쉬카브", "lemma": "שָׁכַב", "morph": "접+동 칼 미완 3남단", "gloss": "그가 누웠다"},
                {"text": "וַיִּישָׁן", "sound": "와예샨", "lemma": "יָशֵׁן", "morph": "접+동 칼 미완 3남단", "gloss": "그가 잠들었다"},
                {"text": "תַּחַת רֹתֶם", "sound": "타하트 로템", "lemma": "רֹתֶם", "morph": "전+명", "gloss": "로뎀 나무 아래"},
                {"text": "וְהִנֵּה־מַלְאָךְ", "sound": "웨힌네-말아크", "lemma": "מַלְאָךְ", "morph": "접+감탄사+명", "gloss": "보라 천사가"},
                {"text": "נֹגֵעַ בּוֹ", "sound": "노게아 보", "lemma": "נָגַע", "morph": "분사 칼+전+접미 3남단", "gloss": "그를 만지고 있다"},
                {"text": "וַיֹּאמֶר", "sound": "와요메르", "lemma": "אָמַר", "morph": "접+동 칼 미완 3남단", "gloss": "그가 말했다"},
                {"text": "קוּם", "sound": "쿰", "lemma": "קוּם", "morph": "동 칼 명령 2남단", "gloss": "일어나라"},
                {"text": "אֱכוֹל", "sound": "에콜", "lemma": "אָכַל", "morph": "동 칼 명령 2남단", "gloss": "먹으라"},
                {"text": "וַיַּבֵּט", "sound": "와야베트", "lemma": "נָבַט", "morph": "접+동 히필 미완 3남단", "gloss": "그가 봤다"},
                {"text": "מְרַאֲשֹׁתָיו", "sound": "메라쇼타이우", "lemma": "מְרַאֲשָׁה", "morph": "명 복+접미 3남단", "gloss": "그의 머리맡에"},
                {"text": "עֻגַת־רְצָפִים", "sound": "우갓-레차핌", "lemma": "עֻגָּה + רֶצֶף", "morph": "명 연계+명 복", "gloss": "구운 떡"},
                {"text": "וְצַפַּחַת מָיִם", "sound": "웨차파하트 마임", "lemma": "צַפַּחַת + מַיִם", "morph": "접+명 연계+명 복", "gloss": "물병"},
                {"text": "וַיֹּאכַל", "sound": "와요칼", "lemma": "אָכַל", "morph": "접+동 칼 미완 3남단", "gloss": "그가 먹었다"},
                {"text": "וַיֵּשְׁתְּ", "sound": "와예쉬트", "lemma": "שָׁתָה", "morph": "접+동 칼 미완 3남단", "gloss": "그가 마셨다"},
                {"text": "וַיָּשָׁב", "sound": "와야솨브", "lemma": "שׁוּב", "morph": "접+동 칼 미완 3남단", "gloss": "그가 돌아왔다"},
                {"text": "וַיִּשְׁכָּב", "sound": "와예쉬카브", "lemma": "שָׁכַב", "morph": "접+동 칼 미완 3남단", "gloss": "그가 누웠다"},
                {"text": "מַלְאַךְ יְהוָה", "sound": "말아크 야훼", "lemma": "מַלְאָךְ + יְהוָה", "morph": "명+고유명", "gloss": "여호와의 천사가"},
                {"text": "쉐니트", "sound": "쉐니트", "lemma": "쉐니", "morph": "형 서수 여단", "gloss": "두 번째로"},
                {"text": "וַיִּגַּع", "sound": "와예가", "lemma": "נָגַע", "morph": "접+동 칼 미완 3남단", "gloss": "그가 만졌다"},
                {"text": "כִּי רַב", "sound": "키 라브", "lemma": "רַב", "morph": "접+형", "gloss": "왜냐하면 많다/크다"},
                {"text": "מִמּךָ", "sound": "밈카", "lemma": "מִן", "morph": "전+접미 2남단", "gloss": "너로부터/너에게는"},
                {"text": "הַדָּרֶךְ", "sound": "하데레크", "lemma": "דֶּרֶךְ", "morph": "관+명", "gloss": "그 길이"}
            ]
        },
        "nt": {
            "ref": "히브리서 2:14-15",
            "lang": "greek",
            "text_dir": "ltr",
            "lang_class": "greek",
            "kor_std": "자녀들은 혈과 육에 속하였으매 그도 또한 같은 모양으로 혈과 육을 함께 지니심은 죽음을 통하여 죽음의 세력을 잡은 자 곧 마귀를 멸하시며 또 죽기를 무서워하므로 한평생 매여 종 노릇 하는 모든 자들을 놓아 주려 하심이라",
            "kor_lit": "그러므로(운) 때문에(에페이) 그 자녀들이(타 파이디아) 나누어 가졌다(케코이노네켄) 피와(하이마토스 카이) 육의(사르코스). 그리고 그분도(카이 아우토스) 비슷하게(파라플레시오스) 나누어 가지셨다(메테스켄) 같은 것들을(톤 아우톤). 그래서(히나) ~ 통하여(디아) 그 죽음을(투 다나투) 그가 파괴하시도록(카타르게세) 그 권세를(토 크라토스) 가지고 있는 자를(에콘타) 그 죽음의(투 다나투) 이것은(투트 에스틴) 그 마귀를(톤 디아볼론). 그리고 해방시키시도록(카이 아팔락세) 이들을(투투스) 얼마든지(호소이) 죽음의 공포로(포보 다나투) ~ 통하여(디아) 모두(판토스) 그 생애에서(투 젠) 종속될 자들이었다(에산 에노호이 둘레이아스).",
            "eng_bsb": "Now since the children have flesh and blood, He too shared in their humanity, so that by His death He might destroy him who holds the power of death, that is, the devil, and free those who all their lives were held in slavery by their fear of death.",
            "focus_text": "ἐπεὶ οὖν τὰ παιδία κεκο인ώνηκεν αἵματος καὶ σαρκός καὶ αὐτὸς παραπλησίως μετέσχεν τῶν αὐτῶν ἵνα διὰ τοῦ θανάτου κατα르게세 톤 토 크라토스 에콘타 투 다나투 투트 에스틴 톤 디아볼론 카이 아팔락세 투투스 호소이 포보 다나투 디아 판토스 투 젠 에산 에노호이 둘레이아스",
            "words": [
                {"text": "에페이 운", "sound": "에페이 운", "lemma": "에페이 + 운", "morph": "접속사+접속사", "gloss": "그러므로 때문에"},
                {"text": "τὰ παιδί아", "sound": "타 파이디아", "lemma": "παιδίο원", "morph": "관+명 주격 중복", "gloss": "그 자녀들이"},
                {"text": "케코인오네켄", "sound": "케코이노네켄", "lemma": "코이노네오", "morph": "동 완료 능동 직설 3복", "gloss": "나누어 가졌다"},
                {"text": "하이마토스 카이 사르코스", "sound": "하이마토스 카이 사르코스", "lemma": "하이마 + 사르크스", "morph": "명 소유격 중단+접+명 소유격 여단", "gloss": "피와 육의"},
                {"text": "카이 아우토스", "sound": "카이 아우토스", "lemma": "아우토스", "morph": "접+대명 주격 남단", "gloss": "그분도 또한"},
                {"text": "파라플레시오스", "sound": "파라플레시오스", "lemma": "파라플레시오스", "morph": "부사", "gloss": "비슷하게"},
                {"text": "메테스켄", "sound": "메테스켄", "lemma": "메테코", "morph": "동 부정과거 능동 직설 3단", "gloss": "나누어 가지셨다"},
                {"text": "톤 아우톤", "sound": "톤 아우톤", "lemma": "아우토스", "morph": "관+대명 소유격 중복", "gloss": "같은 것들을"},
                {"text": "히나", "sound": "히나", "lemma": "히나", "morph": "접속사", "gloss": "~하도록"},
                {"text": "디아 투 다나투", "sound": "디아 투 다나투", "lemma": "디아 + 다나토스", "morph": "전+관+명 소유격 남단", "gloss": "그 죽음을 통하여"},
                {"text": "카타르게세", "sound": "카타르게세", "lemma": "카타르게오", "morph": "동 부정과거 능동 가정 3단", "gloss": "파괴하시도록"},
                {"text": "톤 ... 에콘타", "sound": "톤 에콘타", "lemma": "에코", "morph": "관+분사 현재 능동 대격 남단", "gloss": "가지고 있는 자를"},
                {"text": "토 크라토스", "sound": "토 크라토스", "lemma": "크라토스", "morph": "관+명 대격 중단", "gloss": "그 권세를"},
                {"text": "투 다나투", "sound": "투 다나투", "lemma": "다나토스", "morph": "관+명 소유격 남단", "gloss": "그 죽음의"},
                {"text": "투트 에스틴", "sound": "투트 에스틴", "lemma": "에이미", "morph": "대명+동 현재 능동 직설 3단", "gloss": "이것은 ~이다"},
                {"text": "톤 디아볼론", "sound": "톤 디아볼론", "lemma": "디아볼로스", "morph": "관+명 대격 남단", "gloss": "그 마귀를"},
                {"text": "카이 아팔락세", "sound": "카이 아팔락세", "lemma": "아팔랏소", "morph": "접+동 부정과거 능동 가정 3단", "gloss": "해방시키시도록"},
                {"text": "투투스", "sound": "투투스", "lemma": "후토스", "morph": "지시대명 대격 남복", "gloss": "이들을"},
                {"text": "호소이", "sound": "호소이", "lemma": "호소스", "morph": "관계대명사 주격 남복", "gloss": "얼마든지"},
                {"text": "포보 다나투", "sound": "포보 다나투", "lemma": "포보스 + 다나토스", "morph": "명 여격 남단+명 소유격 남단", "gloss": "죽음의 공포로"},
                {"text": "디아 판토스 투 젠", "sound": "디아 판토스 투 젠", "lemma": "디아 + 파스 + 자오", "morph": "전+형 소유격 남단+관+동 현재 부정사", "gloss": "모든 생애를 통하여"},
                {"text": "에노호이 에산", "sound": "에노호이 에산", "lemma": "에노코스 + 에이미", "morph": "형 주격 남복+동 미완료 능동 직설 3복", "gloss": "종속되어 있었다"},
                {"text": "둘레이아스", "sound": "둘레이아스", "lemma": "둘레이아", "morph": "명 소유격 여단", "gloss": "종노릇의"}
            ]
        },
        "keywords": ["광야", "천사", "공급", "성육신", "해방"]
    }
}

# Output file path
output_file = "/Users/msn/Desktop/MS_Dev.nosync/projects/Kerygma_Daily/Kerygma_Pipeline/02_foundation/week4_foundation.json"

# Write JSON
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(week4_foundation, f, ensure_ascii=False, indent=2)

print(f"✓ Week 4 Foundation (2/7 days) generated: {output_file}")
print("Remaining days: 2026-02-24 to 2026-02-28 (5 days)")
