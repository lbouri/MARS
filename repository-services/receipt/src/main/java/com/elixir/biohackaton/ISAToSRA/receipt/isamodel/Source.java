package com.elixir.biohackaton.ISAToSRA.receipt.isamodel;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.ArrayList;
import lombok.Data;

@Data
public class Source {
  @JsonProperty("@id")
  public String id;

  public String name;
  public ArrayList<Characteristic> characteristics;
}
