import type { Prisma } from "@prisma/client";

import type { ExperimentResult } from "@/lib/datasets";
import { prisma } from "@/lib/prisma";

export function isDatabaseConfigured() {
  return Boolean(process.env.DATABASE_URL);
}

export async function saveExperiment(result: ExperimentResult) {
  const metadata: Prisma.InputJsonValue = {
    rows: result.training_rows + result.testing_rows,
    targetColumn: result.target_column,
  };
  const experimentResult = result as unknown as Prisma.InputJsonValue;
  const config: Prisma.InputJsonValue = { trainSplit: 0.8, randomState: 42 };

  return prisma.experiment.create({
    data: {
      name: `${result.dataset_name.replace(/\.csv$/i, "")} prediction`,
      problemType: result.problem_type,
      targetColumn: result.target_column,
      config,
      result: experimentResult,
      dataset: {
        create: {
          name: result.dataset_name,
          rowCount: result.training_rows + result.testing_rows,
          columnCount: 0,
          metadata,
        },
      },
      modelResults: {
        create: result.models.map((model) => ({
          modelType: model.name,
          metrics: model.metrics as Prisma.InputJsonValue,
          trainingTimeMs: model.training_time_ms,
          featureImportance: result.feature_importance as unknown as Prisma.InputJsonValue,
        })),
      },
    },
    select: { id: true, name: true, createdAt: true },
  });
}

export async function listExperiments() {
  return prisma.experiment.findMany({
    orderBy: { createdAt: "desc" },
    take: 25,
    include: { dataset: true, modelResults: true },
  });
}
