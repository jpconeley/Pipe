export function usd(value: number, digits = 2): string {
  return value.toLocaleString("en-US", { style: "currency", currency: "USD", minimumFractionDigits: digits });
}

export function qty(value: number, unit: string): string {
  return `${value.toLocaleString("en-US")} ${unit}`;
}

export function date(value: string): string {
  return new Date(value).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

export function label(value: string): string {
  return value.replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function sizeLabel(nominalSizeIn: number, scheduleClass: string, grade: string): string {
  return `${nominalSizeIn}" ${scheduleClass} ${grade}`;
}
