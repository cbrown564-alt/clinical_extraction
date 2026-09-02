/** Gan Purist and Pragmatic bands. Thresholds match `labels.py`. */

export function mapPurist(perMonth: number): string {
  if (perMonth === 0) return "currently_no_seizure";
  if (perMonth === 1000) return "seizure_freq_unknown";
  if (perMonth > 0 && perMonth <= 0.16) return "seizure_freq_1_per_yr";
  if (perMonth > 0.16 && perMonth <= 0.18) return "seizure_freq_1_per_6mon";
  if (perMonth > 0.18 && perMonth <= 0.99) return "seizure_freq_more1per6mon_less1mon";
  if (perMonth > 0.99 && perMonth <= 1.1) return "seizure_freq_1_per_mon";
  if (perMonth > 1.1 && perMonth <= 3.9) return "seizure_freq_more1mon_less1week";
  if (perMonth > 3.9 && perMonth <= 4.1) return "seizure_freq_1_per_week";
  if (perMonth > 4.1 && perMonth <= 29) return "seizure_freq_more1week_less1day";
  if (perMonth > 29 && perMonth <= 999) return "seizure_freq_1ormore_daily";
  return "seizure_freq_unknown";
}

export function mapPragmatic(perMonth: number): string {
  if (perMonth === 0) return "currently_no_seizure";
  if (perMonth === 1000) return "seizure_freq_unknown";
  if (perMonth > 0 && perMonth <= 1.1) return "seizure_infrequent";
  if (perMonth > 1.1 && perMonth <= 999) return "seizure_frequent";
  return "seizure_freq_unknown";
}
