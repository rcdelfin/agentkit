# Laravel API: Debugging Missing Data in Responses

When the frontend reports that data is missing (e.g., "Body Parts and Type are not showing"), the root cause is almost never "the model doesn't have it" — it's one of three places in the API layer.

## Debugging Checklist (top to bottom)

### 1. Controller: Are the relations loaded?

If the resource uses `$this->whenLoaded('relation')`, the relation must be eager-loaded **before** passing to the resource.

```php
// ❌ BUG: relation not loaded → whenLoaded returns empty collection
return new ExerciseResource($exercise);

// ✅ FIX: eager-load before returning
return new ExerciseResource(
    $exercise->load(['bodyParts', 'exerciseTypes']),
);
```

**Check both store/update returns and show/index.** It's common to load relations in one endpoint but forget another.

### 2. Resource class: Is the field included?

The resource's `toArray()` must explicitly list the field:

```php
// ✅ Present
'body_parts' => ExerciseReferenceResource::collection($this->whenLoaded('bodyParts')),

// ❌ Missing — entire field is absent from response
```

**Watch for `whenLoaded` with unexpected relation names** — if the relation is named `bodyParts` but `whenLoaded('body_part')` is used (wrong case/pluralization), the condition fails silently and the field is absent.

### 3. Intermediate / parent resource (the most common trap)

When the data is shown **inside a parent** (e.g., exercise inside program day), the parent resource may strip out fields even though the ExerciseResource itself is correct.

```php
// ProgramDayExerciseResource — THE CULPRIT
// Only exposes id + name from the exercise relation
'exercise' => $this->whenLoaded('exercise', fn() => [
    'id' => $this->exercise->id,
    'name' => $this->exercise->name,
    // ❌ body_parts, exercise_types, etc. are MISSING
]),
```

**Fix:** Use the full ExerciseResource instead of a manual array, or explicitly include the missing fields:

```php
'exercise' => new ExerciseResource($this->whenLoaded('exercise')),
// OR
'exercise' => $this->whenLoaded('exercise', fn() => [
    'id' => $this->exercise->id,
    'name' => $this->exercise->name,
    'body_parts' => ExerciseReferenceResource::collection($this->exercise->bodyParts),
    'exercise_types' => ExerciseReferenceResource::collection($this->exercise->exerciseTypes),
]),
```

### 4. Controller eager loading propagates through nesting

A nested relation (e.g., `exercises.exercise.bodyParts`) requires dot-notation in the `load()` call:

```php
// ❌ BUG: bodyParts not available on the nested exercise
$program->load(['weeks.days.exercises.exercise']);

// ✅ FIX: eager-load the nested relations too
$program->load([
    'weeks.days.exercises.exercise',
    'weeks.days.exercises.exercise.bodyParts',
    'weeks.days.exercises.exercise.exerciseTypes',
]);
```

## Quick Diagnostic

When the frontend says "X field is missing":

1. **Check the API response directly** — `dd()` or dump the JSON before returning
2. **Is the field in the model?** — `$this->relationLoaded('relation')` or check the loaded relations
3. **Is the field in the resource?** — Check `toArray()` for the field
4. **Is this response from a parent resource?** — The nested exercise data might be constructed by the parent resource, not the ExerciseResource
