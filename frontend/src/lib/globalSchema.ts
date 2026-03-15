import schemaContract from "../../../shared/global_schema_contract.json";

export type GlobalSchemaField = {
  key: string;
  label: string;
  section: string;
  order: number;
  value_type: "string" | "number" | "boolean" | "date" | "unknown";
  repeatable: boolean;
  critical: boolean;
  optional: boolean;
};

type RawSchemaField = Omit<GlobalSchemaField, "order">;

type RawContract = {
  fields: RawSchemaField[];
};

const parsedContract = schemaContract as RawContract;

export const GLOBAL_SCHEMA: GlobalSchemaField[] = parsedContract.fields.map((field, index) => ({
  ...field,
  order: index + 1,
}));
