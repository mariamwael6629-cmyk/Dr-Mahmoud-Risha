"""
Seed data for the diagnosis/medication/lab-test/radiology autocomplete libraries
and the clinic branding settings (extracted from the doctor's prescription template).
Each library is upserted by its unique name/code so re-running on an already-seeded
database still picks up newly-added catalog entries, without duplicating existing ones.
"""
from database import db
from models.diagnosis import DiagnosisLibrary
from models.medication import MedicationLibrary
from models.lab_radiology import LabTestLibrary, RadiologyLibrary
from models.settings import ClinicSettings

DIAGNOSIS_SEED = [
    # Rheumatology (clinic specialty)
    ("M05", "Rheumatoid Arthritis (seropositive)", "Chronic autoimmune inflammatory arthritis", "Rheumatology"),
    ("M06", "Rheumatoid Arthritis (other)", "Chronic inflammatory joint disease", "Rheumatology"),
    ("M15", "Osteoarthritis, generalized", "Degenerative joint disease affecting multiple joints", "Rheumatology"),
    ("M16", "Osteoarthritis of hip", "Degenerative disease of the hip joint", "Rheumatology"),
    ("M17", "Osteoarthritis of knee", "Degenerative disease of the knee joint", "Rheumatology"),
    ("M10", "Gout", "Crystal-induced arthritis from uric acid build-up", "Rheumatology"),
    ("M32", "Systemic Lupus Erythematosus", "Chronic autoimmune connective tissue disease", "Rheumatology"),
    ("M45", "Ankylosing Spondylitis", "Chronic inflammatory disease of the spine", "Rheumatology"),
    ("M35.3", "Polymyalgia Rheumatica", "Inflammatory condition causing muscle pain/stiffness", "Rheumatology"),
    ("M79.7", "Fibromyalgia", "Chronic widespread musculoskeletal pain", "Rheumatology"),
    ("M06.9", "Juvenile Idiopathic Arthritis", "Arthritis of unknown cause in children", "Rheumatology"),
    ("M65", "Tendinitis", "Inflammation of a tendon", "Rheumatology"),
    ("M75", "Frozen Shoulder (Adhesive Capsulitis)", "Stiffness and pain in the shoulder joint", "Rheumatology"),
    ("M54.5", "Low Back Pain", "Pain localized to the lumbar region", "Rheumatology"),
    ("M25.5", "Joint Pain (Arthralgia)", "Pain in one or more joints", "Rheumatology"),
    ("M81", "Osteoporosis", "Reduced bone density increasing fracture risk", "Rheumatology"),
    ("M02", "Reactive Arthritis", "Arthritis triggered by infection elsewhere in the body", "Rheumatology"),
    ("M30", "Vasculitis", "Inflammation of blood vessels", "Rheumatology"),
    # General / Primary care
    ("I10", "Essential Hypertension", "Chronic elevated blood pressure", "General Medicine"),
    ("E11", "Type 2 Diabetes Mellitus", "Chronic disorder of glucose metabolism", "General Medicine"),
    ("E78", "Hyperlipidemia", "Elevated lipids in the blood", "General Medicine"),
    ("J00", "Common Cold (Acute Nasopharyngitis)", "Viral upper respiratory infection", "General Medicine"),
    ("J02", "Acute Pharyngitis", "Inflammation of the pharynx", "General Medicine"),
    ("J45", "Asthma", "Chronic inflammatory airway disease", "General Medicine"),
    ("J18", "Pneumonia, unspecified", "Infection causing lung inflammation", "General Medicine"),
    ("K21", "Gastroesophageal Reflux Disease (GERD)", "Acid reflux into the esophagus", "General Medicine"),
    ("K29", "Gastritis", "Inflammation of the stomach lining", "General Medicine"),
    ("N39.0", "Urinary Tract Infection", "Bacterial infection of the urinary tract", "General Medicine"),
    ("R51", "Headache", "Pain in the head or upper neck", "General Medicine"),
    ("R50.9", "Fever, unspecified", "Elevated body temperature", "General Medicine"),
    ("E03", "Hypothyroidism", "Underactive thyroid gland", "General Medicine"),
    ("E05", "Hyperthyroidism", "Overactive thyroid gland", "General Medicine"),
    ("D50", "Iron-Deficiency Anemia", "Anemia caused by insufficient iron", "General Medicine"),
    ("L20", "Atopic Dermatitis (Eczema)", "Chronic inflammatory skin condition", "Dermatology"),
    ("L30", "Contact Dermatitis", "Skin inflammation from irritant/allergen contact", "Dermatology"),
    ("G43", "Migraine", "Recurrent moderate-to-severe headache disorder", "Neurology"),
    ("F41.1", "Generalized Anxiety Disorder", "Persistent excessive worry", "Psychiatry"),
    ("F32", "Major Depressive Disorder", "Persistent low mood and loss of interest", "Psychiatry"),
    ("M54.2", "Cervicalgia (Neck Pain)", "Pain localized to the cervical spine", "Orthopedics"),
    ("S93.4", "Ankle Sprain", "Ligament injury of the ankle joint", "Orthopedics"),
]

MEDICATION_SEED = [
    # Rheumatology - DMARDs / Biologics / Steroids
    ("Methotrexate", "Methotrexate", "7.5-25 mg weekly", "DMARD", "First-line for rheumatoid arthritis"),
    ("Plaquenil", "Hydroxychloroquine", "200-400 mg/day", "DMARD", "Used for RA and lupus"),
    ("Sulfasalazine", "Sulfasalazine", "500-1000 mg twice daily", "DMARD", "Used for inflammatory arthritis"),
    ("Arava", "Leflunomide", "10-20 mg/day", "DMARD", "Alternative/add-on DMARD for RA"),
    ("Humira", "Adalimumab", "40 mg every 2 weeks (SC)", "Biologic", "TNF-alpha inhibitor"),
    ("Enbrel", "Etanercept", "50 mg weekly (SC)", "Biologic", "TNF-alpha inhibitor"),
    ("Remicade", "Infliximab", "3-5 mg/kg IV every 8 weeks", "Biologic", "TNF-alpha inhibitor"),
    ("RoActemra", "Tocilizumab", "162 mg weekly (SC)", "Biologic", "IL-6 receptor inhibitor"),
    ("Rituxan", "Rituximab", "1000 mg IV, 2 doses 2 weeks apart", "Biologic", "B-cell depletion for RA/vasculitis"),
    ("Xeljanz", "Tofacitinib", "5 mg twice daily", "JAK inhibitor", "Oral targeted therapy for RA"),
    ("Olumiant", "Baricitinib", "2-4 mg/day", "JAK inhibitor", "Oral targeted therapy for RA"),
    ("Prednisolone", "Prednisolone", "5-60 mg/day", "Corticosteroid", "Anti-inflammatory, taper as needed"),
    ("Cortancyl", "Prednisone", "5-60 mg/day", "Corticosteroid", "Anti-inflammatory"),
    ("Medrol", "Methylprednisolone", "4-48 mg/day", "Corticosteroid", "Anti-inflammatory, also IV pulse therapy"),
    ("Depo-Medrol", "Methylprednisolone Acetate", "40-80 mg intra-articular", "Corticosteroid", "Joint injection for flares"),
    # NSAIDs / Pain
    ("Voltaren", "Diclofenac", "50 mg twice/thrice daily", "NSAID", "Pain and inflammation relief"),
    ("Brufen", "Ibuprofen", "200-400 mg every 6-8h", "NSAID", "Pain and inflammation relief"),
    ("Celebrex", "Celecoxib", "100-200 mg twice daily", "NSAID (COX-2)", "Lower GI risk than non-selective NSAIDs"),
    ("Cataflam", "Diclofenac Potassium", "50 mg twice/thrice daily", "NSAID", "Acute pain relief"),
    ("Mobic", "Meloxicam", "7.5-15 mg/day", "NSAID", "Once-daily anti-inflammatory"),
    ("Arcoxia", "Etoricoxib", "60-120 mg/day", "NSAID (COX-2)", "Pain and inflammation relief"),
    ("Naprosyn", "Naproxen", "250-500 mg twice daily", "NSAID", "Pain and inflammation relief"),
    ("Tramal", "Tramadol", "50-100 mg every 6-8h", "Opioid analgesic", "Moderate-severe pain"),
    ("Lyrica", "Pregabalin", "75-150 mg twice daily", "Neuropathic agent", "Used for fibromyalgia/nerve pain"),
    ("Neurontin", "Gabapentin", "300-900 mg/day", "Neuropathic agent", "Used for neuropathic pain"),
    ("Myonal", "Eperisone", "50 mg three times daily", "Muscle relaxant", "Relieves muscle spasm/back pain"),
    # Gout / Bone
    ("Colchicine", "Colchicine", "0.5 mg 1-2 times daily", "Anti-gout", "Acute gout flare treatment"),
    ("Zyloric", "Allopurinol", "100-300 mg/day", "Anti-gout", "Lowers uric acid"),
    ("Uloric", "Febuxostat", "40-80 mg/day", "Anti-gout", "Lowers uric acid, alternative to allopurinol"),
    ("Fosamax", "Alendronate", "70 mg weekly", "Bisphosphonate", "Osteoporosis treatment"),
    ("Actonel", "Risedronate", "35 mg weekly", "Bisphosphonate", "Osteoporosis treatment"),
    ("Prolia", "Denosumab", "60 mg SC every 6 months", "Bone agent", "Osteoporosis, RANKL inhibitor"),
    ("Calcimax", "Calcium + Vitamin D3", "1 tablet daily", "Supplement", "Bone health support"),
    ("Devarol-S", "Vitamin D3", "50000 IU weekly", "Supplement", "Vitamin D deficiency correction"),
    # General / Antibiotics / Chronic disease
    ("Panadol", "Paracetamol", "500-1000 mg every 6h", "Analgesic", "Pain and fever relief"),
    ("Augmentin", "Amoxicillin/Clavulanate", "625 mg twice/thrice daily", "Antibiotic", "Broad-spectrum infections"),
    ("Zithromax", "Azithromycin", "500 mg once daily x3 days", "Antibiotic", "Respiratory/soft tissue infections"),
    ("Amoxil", "Amoxicillin", "500 mg every 8h", "Antibiotic", "Common bacterial infections"),
    ("Ciprobay", "Ciprofloxacin", "500 mg twice daily", "Antibiotic", "Urinary/GI infections"),
    ("Flagyl", "Metronidazole", "500 mg three times daily", "Antibiotic", "Anaerobic/protozoal infections"),
    ("Concor", "Bisoprolol", "2.5-10 mg/day", "Beta-blocker", "Hypertension/heart rate control"),
    ("Norvasc", "Amlodipine", "5-10 mg/day", "Calcium channel blocker", "Hypertension"),
    ("Capoten", "Captopril", "25-50 mg twice/thrice daily", "ACE inhibitor", "Hypertension"),
    ("Cozaar", "Losartan", "50-100 mg/day", "ARB", "Hypertension"),
    ("Lasix", "Furosemide", "20-80 mg/day", "Diuretic", "Edema/hypertension"),
    ("Glucophage", "Metformin", "500-1000 mg twice daily", "Antidiabetic", "Type 2 diabetes first-line"),
    ("Amaryl", "Glimepiride", "1-4 mg/day", "Antidiabetic", "Type 2 diabetes, sulfonylurea"),
    ("Lantus", "Insulin Glargine", "Per sliding scale (SC)", "Insulin", "Long-acting basal insulin"),
    ("Lipitor", "Atorvastatin", "10-40 mg/day", "Statin", "Cholesterol management"),
    ("Crestor", "Rosuvastatin", "5-20 mg/day", "Statin", "Cholesterol management"),
    ("Nexium", "Esomeprazole", "20-40 mg/day", "PPI", "GERD/gastritis"),
    ("Omeprazole", "Omeprazole", "20-40 mg/day", "PPI", "Acid reflux treatment"),
    ("Claritine", "Loratadine", "10 mg/day", "Antihistamine", "Allergy relief"),
    ("Zyrtec", "Cetirizine", "10 mg/day", "Antihistamine", "Allergy relief"),
    ("Zantac", "Ranitidine", "150 mg twice daily", "H2 blocker", "Acid reduction"),
    ("Ventolin", "Salbutamol", "1-2 puffs as needed", "Bronchodilator", "Asthma relief inhaler"),
    ("Eltroxin", "Levothyroxine", "25-150 mcg/day", "Thyroid hormone", "Hypothyroidism replacement"),
    ("Brufen Cold", "Ibuprofen/Pseudoephedrine", "1 tablet every 8h", "Cold/Flu", "Cold and flu symptom relief"),
    ("Coversyl", "Perindopril", "4-8 mg/day", "ACE inhibitor", "Hypertension"),
    ("Plavix", "Clopidogrel", "75 mg/day", "Antiplatelet", "Cardiovascular protection"),
    ("Aspocid", "Aspirin", "75-100 mg/day", "Antiplatelet", "Cardiovascular protection, low dose"),
    # More Rheumatology - biologics / immunosuppressants
    ("Imuran", "Azathioprine", "50-150 mg/day", "Immunosuppressant", "Used for lupus/vasculitis maintenance"),
    ("Endoxan", "Cyclophosphamide", "Per protocol IV/oral", "Immunosuppressant", "Severe lupus/vasculitis"),
    ("Cellcept", "Mycophenolate Mofetil", "1000-3000 mg/day", "Immunosuppressant", "Lupus nephritis maintenance"),
    ("Sandimmun", "Cyclosporine", "2.5-5 mg/kg/day", "Immunosuppressant", "Refractory autoimmune disease"),
    ("Cosentyx", "Secukinumab", "300 mg every 4 weeks (SC)", "Biologic", "IL-17 inhibitor for spondyloarthritis/psoriatic arthritis"),
    ("Kevzara", "Sarilumab", "200 mg every 2 weeks (SC)", "Biologic", "IL-6 receptor inhibitor"),
    ("Kineret", "Anakinra", "100 mg/day (SC)", "Biologic", "IL-1 receptor antagonist"),
    ("Benlysta", "Belimumab", "10 mg/kg IV every 4 weeks", "Biologic", "B-cell inhibitor for lupus"),
    ("Otezla", "Apremilast", "30 mg twice daily", "PDE4 inhibitor", "Oral therapy for psoriatic arthritis"),
    ("Rinvoq", "Upadacitinib", "15 mg/day", "JAK inhibitor", "Oral targeted therapy for RA"),
    # Anticoagulants / Antiplatelets
    ("Coumadin", "Warfarin", "Per INR target", "Anticoagulant", "Requires regular INR monitoring"),
    ("Clexane", "Enoxaparin", "20-40 mg/day (SC)", "Anticoagulant", "Low-molecular-weight heparin"),
    ("Xarelto", "Rivaroxaban", "10-20 mg/day", "Anticoagulant", "Oral factor Xa inhibitor"),
    ("Eliquis", "Apixaban", "2.5-5 mg twice daily", "Anticoagulant", "Oral factor Xa inhibitor"),
    ("Heparin", "Heparin Sodium", "Per protocol IV/SC", "Anticoagulant", "Acute anticoagulation"),
    # Antifungal / Antiviral
    ("Diflucan", "Fluconazole", "150 mg single dose / 50-100 mg daily", "Antifungal", "Candidiasis treatment"),
    ("Sporanox", "Itraconazole", "100-200 mg/day", "Antifungal", "Fungal infections"),
    ("Lamisil", "Terbinafine", "250 mg/day", "Antifungal", "Dermatophyte/nail infections"),
    ("Canesten", "Clotrimazole", "Apply twice daily", "Antifungal (topical)", "Skin/vaginal fungal infections"),
    ("Zovirax", "Acyclovir", "200-800 mg 5x/day", "Antiviral", "Herpes zoster/simplex"),
    ("Valtrex", "Valacyclovir", "500-1000 mg twice daily", "Antiviral", "Herpes zoster/simplex"),
    ("Tamiflu", "Oseltamivir", "75 mg twice daily x5 days", "Antiviral", "Influenza treatment"),
    # Psychiatric / Neurological
    ("Lustral", "Sertraline", "50-200 mg/day", "SSRI", "Depression/anxiety"),
    ("Prozac", "Fluoxetine", "20-60 mg/day", "SSRI", "Depression/anxiety"),
    ("Cipralex", "Escitalopram", "10-20 mg/day", "SSRI", "Depression/anxiety"),
    ("Xanax", "Alprazolam", "0.25-0.5 mg 2-3x/day", "Benzodiazepine", "Short-term anxiety relief"),
    ("Valium", "Diazepam", "2-10 mg 2-4x/day", "Benzodiazepine", "Anxiety/muscle spasm"),
    ("Zyprexa", "Olanzapine", "5-20 mg/day", "Antipsychotic", "Mood/psychotic disorders"),
    ("Risperdal", "Risperidone", "1-6 mg/day", "Antipsychotic", "Mood/psychotic disorders"),
    ("Stugeron", "Cinnarizine", "25 mg 2-3x/day", "Antivertigo", "Vertigo/motion sickness"),
    # GI / Antiemetic
    ("Primperan", "Metoclopramide", "10 mg 3x/day", "Antiemetic", "Nausea/vomiting"),
    ("Zofran", "Ondansetron", "4-8 mg 2-3x/day", "Antiemetic", "Nausea/vomiting"),
    ("Motilium", "Domperidone", "10 mg 3x/day", "Antiemetic/Prokinetic", "Nausea, GI motility"),
    ("Buscopan", "Hyoscine Butylbromide", "10-20 mg 3x/day", "Antispasmodic", "Abdominal cramps"),
    ("Duspatalin", "Mebeverine", "135 mg 2-3x/day", "Antispasmodic", "Irritable bowel syndrome"),
    ("Imodium", "Loperamide", "2 mg after each loose stool", "Antidiarrheal", "Acute diarrhea"),
    ("Duphalac", "Lactulose", "15-30 ml/day", "Laxative", "Constipation"),
    # Respiratory
    ("Singulair", "Montelukast", "10 mg/day", "Leukotriene antagonist", "Asthma/allergic rhinitis"),
    ("Seretide", "Fluticasone/Salmeterol", "1-2 puffs twice daily", "Inhaled corticosteroid/LABA", "Asthma/COPD maintenance"),
    ("Symbicort", "Budesonide/Formoterol", "1-2 puffs twice daily", "Inhaled corticosteroid/LABA", "Asthma/COPD maintenance"),
    ("Otrivin", "Xylometazoline", "1-2 sprays 2-3x/day", "Decongestant (nasal)", "Nasal congestion, short-term use"),
    # Cardiac
    ("Aldactone", "Spironolactone", "25-100 mg/day", "Diuretic (K-sparing)", "Heart failure/edema/hypertension"),
    ("Tenormin", "Atenolol", "25-100 mg/day", "Beta-blocker", "Hypertension/arrhythmia"),
    ("Lanoxin", "Digoxin", "0.125-0.25 mg/day", "Cardiac glycoside", "Heart failure/atrial fibrillation"),
    ("Nitrolingual", "Glyceryl Trinitrate", "0.4-0.8 mg sublingual PRN", "Nitrate", "Acute angina relief"),
    # Topical / Dermatology
    ("Betnovate", "Betamethasone", "Apply 1-2x/day", "Topical corticosteroid", "Eczema/dermatitis/psoriasis"),
    ("Dermovate", "Clobetasol Propionate", "Apply 1-2x/day", "Topical corticosteroid (potent)", "Severe inflammatory skin disease"),
    ("Bactroban", "Mupirocin", "Apply 2-3x/day", "Topical antibiotic", "Localized skin infections"),
    ("Voltaren Gel", "Diclofenac (topical)", "Apply 3-4x/day", "Topical NSAID", "Localized joint/muscle pain"),
    # Ophthalmology / ENT
    ("Tobrex", "Tobramycin (eye drops)", "1-2 drops 4x/day", "Ophthalmic antibiotic", "Bacterial conjunctivitis"),
    ("Chloramphenicol Eye Drops", "Chloramphenicol", "1-2 drops 4x/day", "Ophthalmic antibiotic", "Bacterial eye infections"),
    ("Timoptol", "Timolol (eye drops)", "1 drop twice daily", "Ophthalmic beta-blocker", "Glaucoma management"),
    # Vitamins / Supplements
    ("Neurobion", "Vitamin B Complex (B1/B6/B12)", "1 tablet/day", "Supplement", "Nerve health/neuropathy support"),
    ("Folic Acid", "Folic Acid", "5 mg/day", "Supplement", "Anemia/pregnancy supplementation"),
    ("Fefol", "Ferrous Sulfate + Folic Acid", "1 capsule/day", "Supplement", "Iron-deficiency anemia"),
    ("Centrum", "Multivitamin/Multimineral", "1 tablet/day", "Supplement", "General nutritional support"),
    ("Omacor", "Omega-3 Fatty Acids", "1 g/day", "Supplement", "Cardiovascular/anti-inflammatory support"),
    # Pediatric formulations
    ("Panadol Syrup", "Paracetamol (suspension)", "Per weight, every 6h", "Analgesic (pediatric)", "Pediatric pain/fever relief"),
    ("Amoxil Suspension", "Amoxicillin (suspension)", "Per weight, 3x/day", "Antibiotic (pediatric)", "Pediatric bacterial infections"),
]

LAB_TEST_SEED = [
    ("CBC", "Complete Blood Count", "Hematology profile screening anemia/infection", "Hematology"),
    ("ESR", "Erythrocyte Sedimentation Rate", "Non-specific marker of inflammation", "Inflammation Marker"),
    ("CRP", "C-Reactive Protein", "Acute-phase inflammation marker", "Inflammation Marker"),
    ("RF", "Rheumatoid Factor", "Autoantibody marker for rheumatoid arthritis", "Autoimmune Marker"),
    ("Anti-CCP", "Anti-Cyclic Citrullinated Peptide", "Specific marker for rheumatoid arthritis", "Autoimmune Marker"),
    ("ANA", "Antinuclear Antibody", "Screening marker for autoimmune/lupus disease", "Autoimmune Marker"),
    ("Anti-dsDNA", "Anti-double-stranded DNA", "Specific marker for systemic lupus erythematosus", "Autoimmune Marker"),
    ("HLA-B27", "HLA-B27 Antigen", "Genetic marker for spondyloarthropathies", "Genetic Marker"),
    ("UA", "Serum Uric Acid", "Used to diagnose/monitor gout", "Metabolic"),
    ("Vit D", "25-Hydroxy Vitamin D", "Bone health and vitamin D deficiency screening", "Bone Profile"),
    ("Ca", "Serum Calcium", "Bone/metabolic and parathyroid screening", "Bone Profile"),
    ("LFT", "Liver Function Tests (ALT/AST/Bilirubin)", "Monitors liver health, esp. before DMARDs", "Liver Profile"),
    ("RFT", "Renal Function Tests (Urea/Creatinine)", "Monitors kidney function", "Renal Profile"),
    ("RBS", "Random Blood Sugar", "Diabetes screening", "Diabetes"),
    ("HbA1c", "Glycated Hemoglobin", "Long-term diabetes control monitoring", "Diabetes"),
    ("Lipid", "Lipid Profile", "Cholesterol/Triglycerides/HDL/LDL panel", "Cardiovascular"),
    ("TSH", "Thyroid Stimulating Hormone", "Thyroid function screening", "Endocrine"),
    ("UA-R", "Urinalysis (Complete)", "General urine analysis", "General"),
    ("Coag", "Coagulation Profile (PT/PTT/INR)", "Bleeding/clotting assessment", "Hematology"),
    ("Ferritin", "Serum Ferritin", "Iron studies, anemia work-up", "Hematology"),
    ("CPK", "Creatine Phosphokinase", "Muscle inflammation/myositis marker", "Muscle Marker"),
    ("C3/C4", "Complement C3 / C4", "Disease activity marker in lupus/vasculitis", "Autoimmune Marker"),
    ("ANCA", "Anti-Neutrophil Cytoplasmic Antibody", "Marker for vasculitis", "Autoimmune Marker"),
    ("Procalcitonin", "Procalcitonin", "Bacterial infection/sepsis marker", "Infection Marker"),
]

RADIOLOGY_SEED = [
    ("XR-KNEE", "X-Ray Knee (AP/Lateral)", "Plain radiograph of the knee joint", "X-Ray"),
    ("XR-HAND", "X-Ray Hands (Bilateral)", "Screens for erosive changes in RA", "X-Ray"),
    ("XR-SPINE", "X-Ray Spine (Full/Lumbosacral)", "Evaluates spinal alignment/degeneration", "X-Ray"),
    ("XR-PELVIS", "X-Ray Pelvis", "Evaluates hip joints/sacroiliac joints", "X-Ray"),
    ("XR-CHEST", "X-Ray Chest", "Baseline lung screening, esp. before biologics", "X-Ray"),
    ("XR-FOOT", "X-Ray Foot (Bilateral)", "Screens for erosive/gouty changes", "X-Ray"),
    ("XR-SI", "X-Ray Sacroiliac Joints", "Used to diagnose ankylosing spondylitis", "X-Ray"),
    ("MRI-LSPINE", "MRI Lumbar Spine", "Detailed imaging of lumbar discs/nerves", "MRI"),
    ("MRI-CSPINE", "MRI Cervical Spine", "Detailed imaging of cervical discs/nerves", "MRI"),
    ("MRI-KNEE", "MRI Knee", "Detailed imaging of ligaments/cartilage", "MRI"),
    ("MRI-SI", "MRI Sacroiliac Joints", "Detects early sacroiliitis", "MRI"),
    ("MRI-SHOULDER", "MRI Shoulder", "Evaluates rotator cuff/joint structures", "MRI"),
    ("CT-CHEST", "CT Chest", "Detailed lung imaging", "CT"),
    ("CT-ABD", "CT Abdomen and Pelvis", "Detailed abdominal/pelvic imaging", "CT"),
    ("US-JOINT", "Ultrasound Joint (Knee/Shoulder/Wrist)", "Detects synovitis/effusion", "Ultrasound"),
    ("US-ABD", "Ultrasound Abdomen", "General abdominal imaging", "Ultrasound"),
    ("DOPPLER", "Doppler Ultrasound (Vascular)", "Evaluates blood flow, screens for vasculitis", "Ultrasound"),
    ("DEXA", "Bone Density Scan (DEXA)", "Diagnoses/monitors osteoporosis", "DEXA"),
    ("MAMMO", "Mammography", "Breast cancer screening", "Mammography"),
    ("CT-SINUS", "CT Sinuses", "Evaluates sinus disease", "CT"),
]


def _upsert(model, key_attr, rows, build_kwargs):
    """Insert any seed rows whose key isn't already present; never touches existing rows."""
    existing = {getattr(r, key_attr) for r in model.query.all()}
    for row in rows:
        kwargs = build_kwargs(row)
        if kwargs[key_attr] not in existing:
            db.session.add(model(**kwargs))


def seed_if_empty():
    """Populate/expand the diagnosis/medication/lab-test/radiology libraries and clinic
    settings. Each catalog is upserted by its unique name/code, so adding new entries to
    the *_SEED lists above and redeploying picks them up even on an already-seeded DB."""
    _upsert(DiagnosisLibrary, "diagnosis", DIAGNOSIS_SEED, lambda row: dict(
        code=row[0], diagnosis=row[1], description=row[2], specialty=row[3]))

    _upsert(MedicationLibrary, "drug_name", MEDICATION_SEED, lambda row: dict(
        drug_name=row[0], generic_name=row[1], dosage=row[2], category=row[3], notes=row[4]))

    _upsert(LabTestLibrary, "test_name", LAB_TEST_SEED, lambda row: dict(
        code=row[0], test_name=row[1], description=row[2], category=row[3]))

    _upsert(RadiologyLibrary, "exam_name", RADIOLOGY_SEED, lambda row: dict(
        code=row[0], exam_name=row[1], description=row[2], category=row[3]))

    if ClinicSettings.query.first() is None:
        # --- NEW FEATURE: branding extracted from the uploaded prescription template ---
        db.session.add(ClinicSettings(
            doctor_name_en="Dr Mahmoud Risha",
            doctor_name_ar="دكتور محمود ريشة",
            clinic_name_en="Dr Risha Rheumatology Clinic",
            clinic_name_ar="عيادة دكتور ريشة لأمراض الروماتيزم",
            specialty_en="Rheumatology Consultant, MD",
            specialty_ar="استشاري الروماتيزم والمفاصل",
            credentials_en="Lecturer of Rheumatology & Immunology — Al Azhar University, Cairo",
            credentials_ar="دكتوراه ومدرس الروماتيزم والمناعة - كلية الطب جامعة الأزهر بالقاهرة\nعضو الجمعية المصرية والأوروبية للروماتيزم",
            address_1="القاهرة - جسر السويس - محطة مترو النزهة - أمام سنترال النزهة أعلي وان جيم",
            address_2="الرحاب - المركز الأول الطبي - عيادات الصفوة",
            phone_1="0100 35 38 198",
            phone_2="0122 80 65 945",
            footer_note_ar="سررنا بلقائكم، نتمنى لكم الشفاء العاجل",
            logo_path="/assets/rx-logo.png",
            signature_path="/assets/rx-signature.png",
            qr_path="/assets/rx-qr.png",
        ))

    db.session.commit()
