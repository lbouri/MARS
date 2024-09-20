package com.elixir.biohackaton.ISAToSRA.receipt.isamodel;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.ArrayList;
import lombok.Data;

@Data
public class DataFile {
  @JsonProperty("@id")
  public String id;

  public String name;
  public String type;
  public ArrayList<Comment> comments;
}
