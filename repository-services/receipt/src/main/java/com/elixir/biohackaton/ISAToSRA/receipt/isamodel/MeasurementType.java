package com.elixir.biohackaton.ISAToSRA.receipt.isamodel;

import lombok.Data;
import lombok.experimental.FieldNameConstants;

@Data
@FieldNameConstants
public class MeasurementType {
  public String annotationValue;
  public String termSource;
  public String termAccession;
}
