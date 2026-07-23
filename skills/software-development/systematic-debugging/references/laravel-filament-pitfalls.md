# Laravel & Filament Debugging Pitfalls

## Filament Resource Routing: Single-Page Resources

A Filament resource with only a custom Page (not ListRecords/EditRecord) must register it as `'index'`, not `'view'`, for the base resource URL to resolve.

```php
// WRONG — causes LogicException: "does not have an [index] page"
public static function getPages(): array
{
    return [
        'view' => ViewCollectionStatus::route('/'),
    ];
}

// CORRECT — 'index' makes the resource URL (/admin/collection-statuses) work
public static function getPages(): array
{
    return [
        'index' => ViewCollectionStatus::route('/'),
    ];
}
```

**Why:** Filament navigates to the `index` route by default when clicking sidebar links or resolving the resource URL. If no `index` page is registered, it throws `LogicException` even if a `view` page exists at the same path (`/`).

**Symptom:** `LogicException: The resource [App\Filament\Resources\XResource] does not have an [index] page. Define [getIndexUrl()] for alternative routing.`

**Fix:** Change the route key from `'view'` to `'index'` in `getPages()`. The page class itself (extending `Filament\Resources\Pages\Page`) doesn't need to change.

## Eloquent Relationship: Method Call vs Dynamic Property

See the main SKILL.md "Framework-Specific Pitfalls" section for the full writeup. Quick reference:

```php
// WRONG — returns BelongsTo object (never null), ?->id accesses relationship, not model
$user->entity()?->id;   // Error: Undefined property: BelongsTo::$id

// CORRECT — dynamic property returns related model or null
$user->entity?->id;     // Returns model->id or null
```

## Frontend Premature API Save (Draft vs Persist Confusion)

When a backend offers a **monolithic create endpoint** (parent + nested children in one call) but the frontend has a **multi-step wizard/builder UI**, the frontend may call the create endpoint on every structural change instead of batching into a local draft.

**Symptom:** Adding a child item (e.g., "Add Week") immediately persists the parent to the database. The parent appears in listings before the user clicks "Save".

**How to spot it:**
1. The bug report says "X action saves/creates Y" when X should only modify UI state
2. Network tab shows a `POST` to the create endpoint on a button that should be draft-only
3. The backend create endpoint accepts nested arrays (weeks, items, children)

**Root cause:** Frontend calls the monolithic API on child-add instead of maintaining local draft state. Often happens because the backend lacks granular child-creation endpoints (`POST /parents/{id}/children`), pushing the frontend toward the monolithic endpoint.

**Fix (frontend):** Keep a reactive draft object. Child-add mutates the draft. Only the explicit "Save" button calls the API. No backend changes needed.

**Fix (backend, if incremental saves are desired):** Add granular endpoints (`POST /parents/{id}/children`) so the frontend can create the parent first, then add children incrementally.

**When investigating "auto-save" bugs:** Always check whether the frontend is calling a create endpoint when it should be modifying local state. Look at the network tab or the button's click handler before diving into backend code.

## Verification Pattern

After fixing Laravel errors, verify with:
1. `php artisan tinker --execute="echo App\Models\User::find(2)->entity?->id ?? 'null';"` — test the specific call
2. `browser_navigate` to the page URL — confirm it loads without error page
3. `tail storage/logs/laravel.log` — confirm no new ERROR entries after page load
