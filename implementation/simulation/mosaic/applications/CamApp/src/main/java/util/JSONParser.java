package util;

import com.google.gson.*;

import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

public class JSONParser {

    private static final Gson gson = new GsonBuilder().setPrettyPrinting().create();

    public static void parseAndWriteJson(String jsonString, String outputFilePath) {
        try {
            File file = new File(outputFilePath);
            JsonArray jsonArray;

            if (file.exists()) {
                try (FileReader reader = new FileReader(file)) {
                    JsonElement element = JsonParser.parseReader(reader);
                    if (element.isJsonArray()) {
                        jsonArray = element.getAsJsonArray();
                    } else {
                        jsonArray = new JsonArray();
                    }
                }
            } else {
                jsonArray = new JsonArray();
            }

            JsonElement newObject = JsonParser.parseString(jsonString);
            jsonArray.add(newObject);

            try (FileWriter writer = new FileWriter(file)) {
                gson.toJson(jsonArray, writer);
            }

        } catch (IOException e) {
            System.err.println("Fehler beim Schreiben der Datei: " + e.getMessage());
            e.printStackTrace();
        } catch (Exception e) {
            System.err.println("Fehler beim Verarbeiten des JSON-Strings: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
