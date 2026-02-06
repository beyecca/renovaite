export interface NamedError {
    name: string;
  }
  
  export function isNamedError(value: unknown): value is NamedError {
    return (
      typeof value === "object" &&
      value !== null &&
      "name" in value &&
      typeof (value as { name: unknown }).name === "string"
    );
  }
  