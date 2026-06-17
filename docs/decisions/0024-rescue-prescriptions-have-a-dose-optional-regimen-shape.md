# Rescue Prescriptions Have a Dose-Optional Regimen Shape

Date: 2026-06-17

For ExECTv2 Prescription component scoring, rescue or PRN anti-seizure medications should have a distinct regimen component shape: medication identity plus `As_Required`, with dose recorded when stated but not required for rescue-regimen credit. The annotation guideline explicitly allows rescue medications without dose, so treating those facts as ordinary complete-tuple failures would misclassify valid Prescription evidence.
