# Literature review ideas and sources

Status: outline only. Not paper prose. C-C-C and IEEE wording come later.
Date: 2026-08-22
Golds: Gan 2026 current-state vs ExECTv2 inventory.
Research object on main: five cells. Each of extract / encode / select is rules, LLM, or both. Headline is the select stop.

## Enough literature?

Yes for the paper. The locked twelve are enough to justify two golds and three named stages.

Yes for supporting, with what is already in `literature/core`. Do not run another broad sweep. Optional later PDFs (only if a supporting subsection needs a named ancestor): Friedman 1994 MedLEE; Chapman NegEx / ConText; Uzuner i2b2 assertion 2010/2011. Not required to start writing.

Do not add neuro-symbolic surveys (Hamilton, Sarker, Garcez) to either document except a one-line “out of scope” if asked.

Supervisor filter: prefer peer-reviewed venues already on the shortlist. Holgate 2024 is ACL BioNLP but weaker than 2025; keep it supporting. Gan 2026 is arXiv; it is one of the two public golds, so it has to stay on the page.

## How to use the marking scheme

Paper (≤1 page, need not fill it): recent/SOTA that *motivates the five cells*. Strengths and limits only where they license extract vs encode vs select, or inventory vs current-state. Gap: later mapping is unnamed and rarely scored as its own stop.

Supporting (30%): in-depth context. Per-article (i) approach (ii) merit/weakness (iii) gap (iv) how this work differs. Families, not a dump of every PDF in `core/`.

---

## 1. One-sentence points

Each line: point. Source. **Paper** or **Support**. Why it matters to this project.

### A. What question prior work asked

1. A clinic letter can contain several true statements; published extractors already choose which to keep. ExECT 2019/2024 vs Xie JAMIA 2022 / Holgate 2025 / Gan 2026. **Paper.** Licenses two golds and the ban on comparing Purist to fact F1.
2. ExECT asks what diagnosis, frequency, prescriptions, and investigations the letter supports (inventory). Fonferko-Shadrach et al. 2019 BMJ Open; 2024 J Biomed Semantics. **Paper.**
3. Xie, Holgate, and Gan ask for one current seizure-frequency state. Xie et al. 2022 JAMIA; Holgate et al. 2025 BioNLP; Gan et al. 2026 arXiv:2603.11407. **Paper.**
4. Fernandes 2024 maps notes onto a questionnaire (daily/weekly/monthly, up to four types, two hospitals). Fernandes et al., Epilepsy Res., 10.1016/j.eplepsyres.2024.107451. **Support.** Shows current-state collapse onto an evaluation form without being a third gold.
5. Holgate 2024 is the zero-shot band paper before the 2025 monthly-number fine-tune; same current-state question, already-collapsed gold. Holgate et al. 2024 BioNLP. **Support.**
6. Abeysinghe 2025 extracts mention-plus-span frequency on EMU reports, not clinic letters. Abeysinghe et al. 2025 npj Digit. Med. **Support.** Closest published inventory-ish frequency system; different document type.
7. Fang 2025 is high-venue epilepsy NLP; frequency is out of scope. Fang et al. 2025. **Support.** Stops the review chasing every epilepsy NLP paper.
8. Yew / “Leveraging pretrained language models for seizure frequency extraction from epilepsy evaluation reports” is another current-state / report-style extractor. On disk in `core/`. **Support.** Extra current-state cousin, not a third question.
9. Zero-shot GPT seizure-outcome papers collapse to a band or outcome label. “Zero-Shot Extraction of Seizure Outcomes…” in `core/`. **Support.** Same collapse; do not spend the page on “LLMs can do frequency.”
10. “Transforming epilepsy research” systematic review maps the field; use it as a supporting map, not a page cite. In `core/`. **Support.**

### B. What they scored (the gold is a form)

11. By MUC-2 the task is template fill against a prepared answer key. Grishman and Sundheim 1996 COLING. **Paper.** Gold is an evaluation form in 1996.
12. Clinical IE automatically extracts and encodes clinical information from text. Wang et al. 2018 JBI. **Paper.** Working definition; licenses encode as a real stage.
13. Mention detection is not concept encoding; a span is not a CUI. Fu et al. 2020 JBI. **Paper.** Find ≠ encode.
14. MedLEE parses to a finding-plus-modifiers frame, then encodes that frame into codes. Friedman et al. 1994 JAMIA (PDF may still need saving). **Support.** Encode is older than LLMs; ancestor of codebook attach.
15. cTAKES / MetaMap / UMLS are the operational ancestors of “attach a codebook id.” Savova 2010; Aronson MetaMap. **Support.** Encode must not look like an LLM trick.
16. Xie 2022 BioNLP extracts the frequency sentence, then rules turn it into a number. Xie, Litt, Roth, Ellis, BioNLP 2022, pp. 369–375. **Paper.** Public encode-then-numeric-revise on the same task family as Gan.
17. Holgate 2024/2025 and many others score a band or a monthly number, not the letter. **Paper (2025) / support (2024).** The scored object is already collapsed.
18. i2b2 assertion scores present / absent / possible / hypothetical / conditional / someone else as its own task. Uzuner et al. 2011 JAMIA. **Support.** Uncertainty is a scored category, not noise.
19. Score projections can discard distinctions that remain in the recorded object. This project’s hop log vs Purist / fact F1. **Paper methods, not a lit cite.** Mention in supporting if explaining why headline ≠ extract stop.

### C. Notes are written that way on purpose

20. Narrative expressivity carries impression, reasoning, concern, and uncertainty to the next clinician; structure that kills it is a loss. Rosenbloom et al. 2011 JAMIA. PDF in `core/` (`Data from clinical notes…`). **Support**, one clause on the paper only if the intro needs “why letters look like this.”
21. Hedge phrases are justified by inherent uncertainty; notes were written for other clinicians, not patients. Zhou, Trivedi, Elhadad 2012; Prince, Frader, Bosk 1982. Hedging PDF in `core/`. **Support.**
22. “Bad” clinic records have good organizational reasons; they are instruments of the work. Garfinkel 1967; Berg 1996. **Support only.** Do not spend a paper ref.
23. Copy-paste and billing bloat are workflow rot, not the same fact as designed hedging. **Support.** Keep the two stories apart.

### D. Hybrids already exist; they do not stop the stack

24. Industry kept rule-based IE while academia hid rules as “constraints” or “dictionaries.” Chiticariu, Li, Reiss 2013 EMNLP. **Paper.** Why this paper names encode and select.
25. Agrawal et al. 2022 define a resolver that maps model text onto the evaluation form and report GPT-3 vs GPT-3+resolver. EMNLP 2022, pp. 1998–2022. **Paper.** Closest published “later stage scored apart.”
26. Prenosil 2025 is ledger-then-rules and reports model-only vs combined, without naming encode vs select. *Commun. Med.* PDF in `core/`. **Support.**
27. Liu 2026 uses rules as a high-recall front filter, then an LLM classifies (statin barriers). IJMI 205:106104. PDF in `core/` and Downloads. **Support.** Foil: their rules decide whether the model runs; yours decide what happens to an extract.
28. Dao 2025 puts schema and guardrails in the prompt and retries; the model still owns encode and revise. JAMIA Open 2025. PDF in `core/`. **Support.** Foil: schema-in-prompt ≠ recorded encode.
29. Geng 2023 is grammar-constrained decoding: schema as a formal constraint, not clinical authority. EMNLP 2023. PDF in `core/`. **Support.** Transport rules / format.
30. “Are we ready to switch to LLMs” and similar switch papers headline one number. PDF in `core/`. **Support.** The frame this paper refuses.
31. Neuro-symbolic surveys exist; they are a different literature. Hamilton / Sarker / Garcez; `Neuro Symbolic AI Review.pdf` in `core/`. **Out of scope.** Do not open on the page or as a supporting chapter.

### E. Transfer, corpora, synthetic gold

32. Decker 2022: seizure-frequency F1 0.82 in-house, 0.40 at a second centre. *Seizure* 101:48–51. **Paper, one clause.** Rule transfer is not free; not the spine; not an argument against recorded rules.
33. Most epilepsy extractors use one private or local corpus. Implied by ExECT, Xie, Decker, Holgate. **Paper, one clause.**
34. Gan 2026 builds a public synthetic current-state gold so the form can be studied without sharing letters. arXiv:2603.11407. **Paper** as a gold, not as a method model.
35. Synthetic-notes utility papers (e.g. “Are synthetic clinical notes useful…”) are supporting only. **Support.**
36. LLM transfer evidence is thin; do not claim models transfer better unless a paper says so. **Paper caution.**

### F. Rule-system organisation (methods/supporting, not the review spine)

37. MedLEE: small semantic grammar, growing lexicon, finding+modifier frame, then encode. Friedman 1994/2004. **Support** (methods / rule catalogue).
38. ConText: one engine (trigger, window, scope), many lists. Chapman et al. **Support.**
39. FASTUS: cascade of small objects then larger ones. Hobbs et al. 1997. **Support.** Replay order story (extract → encode → select).
40. SystemT / AQL: named operators with typed I/O. Chiticariu line. **Support** plus the page Chiticariu cite. Matches the authority index (parse, dialect, projection, gate, rewrite, reselect, invent).
41. This project’s live stack is flattened by iterative tuning; organise the *description* (authority → tables → two gold frames), do not recode. Decision on main. **Methods/supporting**, not a lit point.

### G. What this project does that the literature does not

42. Same three stage names on two golds that already ask different questions. **Paper contribution.**
43. Five cells: who runs extract, encode, and select (rules / LLM / both). Headline is select. Extract and encode are prior-stage ablations. README 2026-08-22. **Paper contribution.**
44. Cell 3 (LLM / rules / rules) is the six-model roster row; cell 4 is a different hop on ExECT (later encode call) than on Gan (extract already wrote the form). **Paper methods.** Literature can still call both encode; methods must say they are not the same hop.
45. Recorded hops keep source span and the change log, not only the score. **Paper closer.**
46. Claim boundary remains textual presence; 48-item semantic-support review stays unset. **Paper/methods.** Literature on hedging does not license reading unstated meaning.

---

## 2. Paper vs supporting

### Paper (about 12 cites; ≤1 page; do not fill the page for its own sake)

Must appear:

| Key | Item | Job on the page |
| --- | --- | --- |
| b1, b2 | ExECT 2019, 2024 | Inventory question |
| b3 | Xie 2022 JAMIA | Current-state question |
| b4 | Holgate 2025 | Current-state, recent SOTA |
| b5 | Gan 2026 | Current-state gold used here |
| b6 | Fu 2020 | Find ≠ encode |
| b7 | Grishman 1996 | Gold is a form |
| b8 | Wang 2018 | Extract and encode |
| b9 | Xie 2022 BioNLP | Public encode then number |
| b10 | Agrawal 2022 | Later stage scored apart |
| b11 | Chiticariu 2013 | Name the rules |
| b12 | Decker 2022 | Transfer clause only |

Optional one-clause on the page, no extra cite if space dies: letters hedge and corefer because they are written for another clinician (Rosenbloom already in `core/`).

Paper must **not** do: rules vs LLM vs hybrid as three equal methods; neuro-symbolic genealogy; IAA theatre; “LLMs are promising”; Decker as the spine; comparing F1 across golds; Liu/Dao as “first hybrid” foil on the page.

### Supporting (deeper review)

Write as short families, each article with (i)–(iv):

1. **Two questions, more cousins** — Fernandes, Holgate 2024, Abeysinghe, Fang, Yew/EMU-report extractors, zero-shot outcome papers, epilepsy NLP systematic review.
2. **Definition and ancestry** — Friedman/MedLEE, Meystre 2008 (`Extracting Information from Textual Documents…` in `core/`), cTAKES, MetaMap, NegEx/ConText, i2b2 assertion.
3. **Why the letter looks like that** — Rosenbloom 2011, Zhou/Elhadad hedging, Prince 1982, Garfinkel/Berg (one page max).
4. **Hybrids that did not stop the stack** — Prenosil, Liu 2026, Dao 2025, Geng 2023, “ready to switch to LLMs.”
5. **Rule organisation patterns** — MedLEE frames, ConText tables, FASTUS cascade, SystemT operators; how they apply to the catalogue without recoding.
6. **Corpora and synthetic gold** — private-corpus limit, Gan synthetic rationale, synthetic-note utility papers.
7. **Explicit out of scope** — neuro-symbolic surveys; multi-agent clinical IE (CLINES, etc.) unless a sentence is needed to say this is not that.

---

## 3. Narrative that motivates the research

Build the paper page in this order. Each beat is one claim. Because/consequence later.

1. Letters contain several true statements. Prior work already picked a question: inventory or current state. That is why this project uses two public golds and never moves a score between them.
2. Whatever question they picked, they scored a designed form (template, codebook, band, number). Wang/Grishman/Fu make that the definition of clinical IE. Encode is that step. A span is not proof the right statement was chosen.
3. Someone still has to change or keep the fact after the form is written. That is select. Almost nobody names it. Xie BioNLP does encode-then-number in public. Agrawal scores a resolver. Chiticariu is why the rest of the field hid the rest of the rules.
4. Hybrids and local rule stacks already exist. Decker shows a local stack need not transfer. That is a caution, not the research question.
5. Gap: prior work did not stop the stack on two different questions and say which later rule only wrote the form and which later rule changed the fact.
6. This work: five cells, same stage names on both golds, headline at select, extract/encode as ablations, hop log kept.

Supporting narrative: same spine, then deepen each family with merits/weaknesses (rules: controllable, style-bound; LLMs: paraphrase, hard to attribute; hybrids: already common, still one headline number). End each family with how the five-cell stop differs.

Do not motivate with “doctors write badly” or “LLMs are the new SOTA so we hybridise.” Motivate with an unnamed stage on two already-published questions.

---

## 4. Suggested paper-page skeleton (beats, not prose)

Target: ~3/4 page. Four short paragraphs, not three.

1. Two questions (points 1–3). Cite b1–b5. Close with Fu b6.
2. IE is fill-this-form (points 11–13, 16–17). Cite b7, b8, b6, b9.
3. Later mapping is a named step and is usually hidden (points 24–25). Cite b10, b11. One sentence on encode vs select.
4. Local corpora / Decker clause / what this work does (points 32–33, 42–45). Cite b12.

If the supervisor wants “strengths and limitations” more visibly: fold one sentence into para 2 (rules write a form well, fail when the fact must be chosen) and one into para 3 (models collect paraphrase, fail at attribution unless a resolver is scored).

---

## 5. Sources already on disk (do not re-download)

Page PDFs should be in `literature/core/` or `core/key/`.

Also already in `core/` and reserved for supporting: Rosenbloom 2011; Meystre-style EHR IE review; Holgate 2024 (`Extracting epilepsy-related information…` / Llama 2 marked BAD PAPER if that copy is the weak one — use the BioNLP 2024 file, not the marked copy); Prenosil 2025; Geng 2023; Liu 2026; Dao 2025; hedging; epilepsy NLP systematic review; Agrawal (`LLMs are Few-Shot Clinical Information Extractors.pdf`); Chiticariu (`Rules are dead. Long live rules.pdf`); Fu; Wang; Grishman; Xie BioNLP.

---

## 6. Still thin (optional, not blocking)

- Friedman 1994 JAMIA MedLEE (OA via PMC) if supporting ancestry is written out.
- Chapman NegEx 2001 / ConText 2007 if assertion lists are discussed.
- Uzuner 2011 i2b2 concepts/assertions/relations if “uncertainty is a scored category” needs a cite.
- Confirm Fernandes 2024 PDF if that cousin paragraph is written.

No further search for “LLM clinical IE 2024–2026” unless the supervisor demands a longer SOTA list. Those papers fight the framing if they land on the page.
