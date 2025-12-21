package util;

import java.io.*;

public class SerializationUtils {

    public static byte[] toBytes(Serializable obj) throws IOException {
        try (ByteArrayOutputStream bos = new ByteArrayOutputStream();
             ObjectOutputStream  oos = new ObjectOutputStream(bos)) {
            oos.writeObject(obj);
            oos.flush();
            return bos.toByteArray();
        }
    }

    @SuppressWarnings("unchecked")
    public static <T> T fromBytes(byte[] data) throws IOException, ClassNotFoundException {
        try (ByteArrayInputStream  bis = new ByteArrayInputStream(data);
             ObjectInputStream     ois = new ObjectInputStream(bis)) {
            return (T) ois.readObject();
        }
    }
}

