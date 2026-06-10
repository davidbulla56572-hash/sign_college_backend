---
name: frontend-phase-implementation
description: Systematic methodology for implementing a new development phase/spec in a React + TypeScript + TanStack Query frontend, from spec ingestion to verified build.
source: auto-skill
extracted_at: '2026-06-09T23:15:00.000Z'
---

## Purpose

When given a phase specification document (e.g., `fase_13_validacion_admin_items_trazabilidad.md`) to implement in a React/TypeScript frontend that consumes a FastAPI backend, use this systematic approach to ensure complete, coherent delivery that matches existing project patterns.

## Procedure

### 1. Ingest the spec

- Read the phase document in full.
- Extract the **expected endpoints** the frontend must call.
- Extract the **expected response contracts** (JSON examples).
- Extract the **frontend-specific requirements** (components, hooks, pages, UX flows).
- Extract the **DoD criteria** (what "done" means for the frontend).

### 2. Explore the existing frontend thoroughly

Before creating anything, explore the frontend project to understand:

- **File structure**: How features are organized (`features/*/api/`, `features/*/hooks/`, `features/*/components/`, `features/*/pages/`).
- **API client**: How `httpClient` is configured (base URL, interceptors, auth injection).
- **Hook patterns**: How TanStack Query hooks are written (queryKey naming, `enabled` conditions, mutation invalidation).
- **Component patterns**: Naming conventions (PascalCase), styling (Tailwind, `cn()` utility), loading/error states.
- **Routing**: How routes are defined, how params are extracted (`useParams`), how navigation works (`useNavigate`).
- **Color/theme tokens**: Brand colors, state badge patterns, common utility classes.
- **Type patterns**: Whether types are defined inline in `.api.ts` files or in separate `types/` files.
- **State management**: What uses Zustand vs. TanStack Query vs. local `useState`.

Use `list_directory` and `read_file` on key files:
- `features/<relevant-feature>/api/*.api.ts`
- `features/<relevant-feature>/hooks/*.hooks.ts`
- `features/<relevant-feature>/pages/*.tsx`
- `features/<relevant-feature>/components/*.tsx`
- `lib/api/httpClient.ts`
- `app/router/AppRouter.tsx`
- `lib/utils/cn.ts`

### 3. Map spec to frontend artifacts

For each spec requirement, determine which frontend layer it affects:

| Spec concern | Frontend layer |
|---|---|
| API calls | `features/<feature>/api/<feature>.api.ts` |
| Data fetching / mutations | `features/<feature>/hooks/<feature>.hooks.ts` |
| Page / view | `features/<feature>/pages/<Feature>Page.tsx` |
| Reusable UI pieces | `features/<feature>/components/<Component>.tsx` |
| Route definition | `app/router/AppRouter.tsx` |
| Types | Inline in `.api.ts` or `types/<feature>.types.ts` |

### 4. Implement in order

Follow this sequence to avoid import errors and rework:

| Step | Layer | What to do |
|---|---|---|
| 1 | Types | Add new TypeScript types to the `.api.ts` file matching the backend response contracts exactly. |
| 2 | API methods | Add `httpClient.get/post/patch` calls that hit the new backend endpoints. Export them. |
| 3 | Hooks | Create `use*Query` and `use*Mutation` hooks following the existing pattern. Include proper `queryKey`, `enabled`, cache invalidation, and toast notifications. |
| 4 | Components | Build small, focused components following existing styling patterns (Tailwind, `cn()`, brand colors, badge styles). |
| 5 | Page | Assemble the page that integrates all components, uses the hooks, handles loading/error states. |
| 6 | Route | Add the route in `AppRouter.tsx` with appropriate protection (role guards). |
| 7 | Navigation links | Update existing tables/lists to link to the new page (e.g., make rows clickable, add "Ver detalle" buttons). |

### 5. Type design rules

- **Mirror backend contracts**: Types must match the Pydantic response schemas field-for-field.
- **Use `| null` for optional server fields**, not `?` — the backend sends `null`, not `undefined`.
- **Keep types inline** in the `.api.ts` file if that's the project pattern; don't create separate type files unless the project already does.
- **Export types** that are used by hooks, components, or other features.

### 6. Hook design rules

Follow the existing project pattern exactly:

```typescript
// Query hook
export function useXxxQuery(id: number) {
  return useQuery({
    queryKey: ["feature", "subkey", id],
    queryFn: () => apiMethod(id),
    enabled: id > 0,
  });
}

// Mutation hook
export function useXxxMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: apiMethod,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["feature"] });
      toast.success("Operation success message");
    },
    onError: () => {
      toast.error("Error message");
    },
  });
}
```

- **queryKey hierarchy**: `["feature", "resource", action?, id]` — match existing patterns.
- **Invalidation**: Invalidate the most specific query first, then broader ones.
- **Toast messages**: Always provide success and error toasts in Spanish (matching project locale).

### 7. Component design rules

- **Naming**: PascalCase, functional components.
- **Styling**: Tailwind CSS exclusively. Use `cn()` for conditional classes.
- **Brand colors**: Use project-specific tokens (`text-brand-700`, `bg-brand-700`, etc.).
- **State badges**: Match existing `estadoLabels` and `estadoColors` maps.
- **Loading state**: `<div className="flex items-center justify-center py-12"><p className="text-sm text-gray-500">Cargando...</p></div>`
- **Empty state**: Inline message or `<EmptyState>` component.
- **Tables**: `rounded-lg border border-gray-200 bg-white shadow-soft` wrapper, `divide-y divide-gray-200` rows.
- **Props**: Define types inline or at top of file. Use `Props` type alias.

### 8. Page design rules

- **Loading first**: Check `isLoading` and show loading state before rendering content.
- **Null check**: If data is undefined/null, show empty/error state.
- **Use `useParams`** for route params, `useNavigate` for navigation.
- **Keep logic in hooks**: The page should primarily compose components and hooks, not contain business logic.

### 9. Navigation integration

When a new detail page is created:

- Make existing table rows clickable (`onClick={() => navigate(`/path/${id}`)}`).
- Add `cursor-pointer` class to clickable rows.
- Or add explicit action buttons ("Ver revision", "Ver detalle").
- Ensure the back button on the detail page navigates to the appropriate parent view.

### 10. Verify build

Run these checks before declaring done:

```bash
# Type check (zero errors expected)
npx tsc --noEmit

# Production build (must succeed)
npx vite build
```

If either fails, fix the errors before declaring the phase complete.

## Key principles

- **Explore before you build**: Never assume patterns. Read existing files first.
- **Match, don't innovate**: Use the exact same hook patterns, component styles, and type conventions already in the project.
- **Types first**: You can't write API methods or hooks without knowing the types.
- **Small components**: Build focused, reusable pieces (toggle, list, header, card) and compose them in the page.
- **Navigation is part of completeness**: A page that exists but isn't linked from anywhere is incomplete.
- **Verify at every step**: Don't wait until the end to type-check. Check after types, after hooks, after components.
- **Backend must be ready**: The frontend assumes the backend endpoints exist and return the expected contracts. If the backend isn't ready, note the dependency.
