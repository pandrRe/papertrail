export function countryCodeToFlagEmoji(code: string): string {
  if (!code || code.length !== 2) {
    throw new Error("Country code must be a 2-letter ISO 3166-1 alpha-2 code.");
  }

  // Unicode Regional Indicator Symbols start at 0x1F1E6 ("A")
  const OFFSET = 0x1f1e6 - "A".charCodeAt(0);

  return code
    .toUpperCase()
    .split("")
    .map((char) => String.fromCodePoint(char.charCodeAt(0) + OFFSET))
    .join("");
}
