import js from "@eslint/js";
import tseslint from "typescript-eslint";
import prettier from "eslint-config-prettier";
import importPlugin from "eslint-plugin-import";

export default tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["**/*.ts"],
    ignores: ["dist", "coverage", "node_modules", "src/examples", "vitest.config.ts"],
    languageOptions: {
      parser: tseslint.parser,
      parserOptions: {
        project: "./tsconfig.json",
        tsconfigRootDir: import.meta.dirname,
        sourceType: "module"
      }
    },
    plugins: { import: importPlugin },
    rules: {
      "import/order": ["error", { "newlines-between": "always" }],
      "@typescript-eslint/consistent-type-imports": "error",
      "@typescript-eslint/no-floating-promises": "warn",
      "@typescript-eslint/no-explicit-any": "warn",
      "no-console": "off"
    }
  },
  {
    files: ["src/__tests__/**/*.test.ts"],
    rules: {
      "@typescript-eslint/no-explicit-any": "off",
      "@typescript-eslint/no-unused-vars": "off"
    }
  },
  prettier
);